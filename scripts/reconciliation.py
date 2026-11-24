"""Close an interrupted operation by recording the explicitly retained readback."""
import json
from shared_state import canonical, fingerprint, require, timestamp, validate, index

RESOLUTION = "KEPT_OBSERVED_STATE"

def prior_digest(rows):
    return fingerprint(sorted((r["id"], fingerprint(r)) for r in rows))

def is_closed(rows):
    markers = [r for r in rows if r["result"] == RESOLUTION and r["event"] == "CONFLICT"]
    if len(markers) != 1:
        return False
    marker = markers[0]
    prior = [r for r in rows if r["id"] != marker["id"]]
    try:
        data = json.loads(marker["changes_json"])
        return (bool(prior) and any(r["event"]=="PREPARED" for r in prior)
                and data["prior_sha256"] == prior_digest(prior)
                and marker["last_op_id"] == marker["op_id"]
                and data["resolution"] == RESOLUTION and bool(data["reason"].strip())
                and bool(marker["authorization_ref"].strip())
                and all(len(data[k]) == 64 and all(c in "0123456789abcdef" for c in data[k])
                        for k in ("intended_changes_sha256","observed_targets_sha256"))
                and timestamp(marker["updated_at"]) >= max(timestamp(r["updated_at"]) for r in prior))
    except (TypeError, KeyError, ValueError, AttributeError):
        return False

def reconcile(plan, fresh, authorization):
    """Propose one journal append. Never roll back, rewrite business data, or claim success."""
    validate(fresh)
    require(fresh["spreadsheet_id"] == plan["spreadsheet_id"], "Wrong reconciliation spreadsheet")
    rows = [r for r in fresh["tables"]["Revision History"] if r["op_id"] == plan["op_id"]]
    prepared = [r for r in rows if r["event"]=="PREPARED"]
    require(prepared and not any(r["result"]==RESOLUTION for r in rows), "No pending preparation to reconcile")
    require(not (any(r["event"]=="CONFIRMED" for r in rows) and
                 not any(r["event"] in {"CONFLICT","INCOMPLETE"} for r in rows)),
            "Operation already has a confirmation; verify the receipt first")
    require(all(r["actor"]==plan["actor"] and r["authorization_ref"]==plan["authorization_ref"]
                for r in prepared), "Operation identity differs from original preparation")
    from history_integrity import ensure_preserved
    from journal_codec import decode_event
    ensure_preserved(plan, fresh["tables"]["Revision History"])
    try:
        recorded = decode_event(prepared)
    except (TypeError,ValueError,KeyError):
        # Each surviving segment must be one expected segment of the supplied plan.
        from journal_codec import change_payloads
        expected = set(change_payloads(plan["changes"]))
        require(all(canonical(json.loads(r["changes_json"])) in expected for r in prepared),
                "Available journal parts differ from the original plan")
    else:
        require(recorded == plan["changes"], "Prepared changes differ from original plan")
    require(authorization.get("authorized") is True and authorization.get("decision")==RESOLUTION
            and all(isinstance(authorization.get(k),str) and authorization[k].strip()
                    for k in ("user_message_ref","actor","reason","at")), "Explicit reconciliation decision required")
    require(timestamp(authorization["at"]) >= timestamp(fresh["read_at"]) >=
            max(timestamp(r["updated_at"]) for r in rows), "Reconciliation needs a current independent read")
    observed = observed_versions(plan, fresh)["observed"]
    require(authorization.get("observed_targets_sha256")==fingerprint(observed),
            "Review the observed versions and authorize their exact fingerprint")
    data = {"resolution":RESOLUTION,"reason":authorization["reason"],"prior_sha256":prior_digest(rows),
            "intended_changes_sha256":fingerprint(plan["changes"]),"observed_targets_sha256":fingerprint(observed)}
    marker = {**prepared[0],"id":plan["op_id"]+"-RECONCILED","updated_at":authorization["at"],
              "updated_by":authorization["actor"],"actor":authorization["actor"],"event":"CONFLICT",
              "authorization_ref":authorization["user_message_ref"],"changes_json":canonical(data),"result":RESOLUTION,
              "evidence_ref":authorization["user_message_ref"]}
    require(not any(r["id"]==marker["id"] for r in fresh["tables"]["Revision History"]), "Reconciliation marker already exists")
    return {"kind":"JOURNAL_APPEND_PROPOSAL","observed":observed,"row":marker,"atomic":False}

def observed_versions(plan, fresh):
    validate(fresh)
    require(plan["spreadsheet_id"]==fresh["spreadsheet_id"],"Wrong reconciliation spreadsheet")
    ix=index(fresh)
    observed=[]
    for c in plan["changes"]:
        row=ix[c["table"]].get(c["id"])
        observed.append({"table":c["table"],"id":c["id"],"current_sha256":fingerprint(row),
                         "state":"BEFORE" if row==c["before"] else "AFTER" if row==c["after"] else "DIFFERENT"})
    return {"observed":observed,"observed_targets_sha256":fingerprint(observed),"saved":False}
