"""Bind creative approvals to the declared deliveries before planning a write."""
import copy
import hashlib
import json
from pathlib import Path

from judgment import validate_review
from shared_state import ASSETS, ROOT, StateError, canonical, fingerprint, require


CREATIVE_GATES = {"G2","G3","G4","G5","G7","G8","G9","G10","G11","G13","G14"}
PRODUCTION_TABLES = ASSETS | {"Artifact Registry"}
APPROVED = {"APPROVED", "LOCKED"}
DEPARTMENTS = {
    "Screenplays": {"story","screenplay","dialogue","emotion","suspense","retention"},
    "Characters": {"casting","character-sheets","performance-sheets","performance","wardrobe"},
    "Locations": {"locations","geometry","atmosphere","living-world","composition","lighting"},
    "Props": {"props","continuity"},
    "Cinematography": {"photography","optics","composition","lighting","color-texture",
                       "atmosphere","direction","sound","editing"},
    "Shot List": {"direction","shot-design","storyboards","continuity","performance"},
    "Prompts": {"prompts"},
}


def declarations(raw):
    """Plain IDs remain valid input. New receipts store all material pins."""
    require(isinstance(raw, str) and raw.strip(), "Gate needs explicit delivery IDs before approval")
    raw = raw.strip()
    if raw.startswith(("[", "{")):
        try:
            items = json.loads(raw)
        except ValueError as e:
            raise StateError("Malformed delivery reference JSON") from e
        if isinstance(items, dict):
            require(items.get("format") == "cpe-deliveries-1", "Unknown delivery manifest")
            items = items.get("targets")
    else:
        items = [raw]
    require(isinstance(items, list) and bool(items), "Gate delivery list empty")
    result = {}
    for item in items:
        item = {"id":item} if isinstance(item, str) else item
        require(isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()
                and set(item) <= {"table","id","revision","record_sha256","sha256"},
                "Invalid delivery pin")
        require(item["id"] not in result, "Duplicate declared delivery")
        result[item["id"]] = item
    return result


def file_sha256(path):
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def content_matches(table, row, target):
    """Use bytes of registered media, inline text, bound local source, or full record."""
    if table == "Artifact Registry":
        return row["sha256"] == target["sha256"]
    field = {"Screenplays":"text_or_ref","Prompts":"prompt_text",
             "Characters":"asset_ref","Props":"asset_ref","Locations":"asset_ref"}.get(table)
    material = row.get(field, "") if field else ""
    checksum = target["sha256"]
    uri = target.get("uri")
    # An external review packet cannot silently substitute an entirely different file.
    if material and uri and isinstance(uri, str):
        locator = material.partition("#")[0]
        try:
            source = Path(locator)
            path = Path(uri).resolve()
            candidates = {(ROOT / source).resolve(), source.resolve()}
            if path in candidates and path.is_file():
                return file_sha256(path) == checksum
        except (OSError, ValueError):
            pass  # Inline prose may be too long to be a native file name.
    if table in {"Screenplays","Prompts"} and material:
        if uri and Path(uri).suffix and material.strip() == uri.strip():
            return False  # Missing external file cannot be approved as its path string.
        if material.lstrip().lower().startswith(("https://","http://","file://","drive:")):
            return False   # Register verified external bytes and approve that registry ID.
        if len(material) < 512 and "\n" not in material and Path(material.partition("#")[0]).suffix.lower() in {".md",".txt",".pdf",".docx",".fountain",".fdx",".json",".html",".rtf"}:
            return False
        # Legacy packet fixtures fingerprinted the canonical JSON string; both
        # allowed digests are derived exclusively from this exact inline text.
        return checksum in {hashlib.sha256(material.encode("utf-8")).hexdigest(), fingerprint(material)}
    return not material and checksum == fingerprint(row)


def check_direct_binding(snapshot, intent, assets, direct, checked, approving_gate):
    """An earlier gate approval belongs only to the work listed in its receipt."""
    tables = snapshot["tables"]
    approval_rows = {r["id"]:r for r in tables["Approvals"]}
    for change in intent["changes"]:
        if change["table"] == "Approvals":
            approval_rows[change["id"]] = {**approval_rows.get(change["id"],{}), **change["values"]}
    for key in direct:
        table, row = assets[key]
        patch = next(c["values"] for c in intent["changes"] if c["id"] == key)
        if table == "Artifact Registry":
            approval_id = patch.get("approval_id", row.get("approval_id"))
            approval = approval_rows.get(approval_id)
            require(approval is not None, "Registered asset approval requires a recorded human decision")
            gate = next((w for w in tables["Workflow"] if w["id"] == approval["workflow_id"]), None)
        else:
            gate = next((w for w in tables["Workflow"] if w["episode_id"] == row["episode_id"]
                         and w["gate_id"] == row["gate_id"]), None)
        require(gate is not None, "Missing department approval")
        if approving_gate and gate["id"] == approving_gate["id"]:
            if table == "Artifact Registry":
                require(approval["gate_revision"] == gate["revision"] + 1,
                        "Registry decision must refer to the gate version being approved")
            continue  # The full declared set and every current review are checked in this operation.
        require(gate["status"] in APPROVED, "A current gate approval must cover this material")
        gate_targets = declarations(gate["deliverable_ref"])
        require(key in gate_targets, "Human gate decision covers a different delivery")
        pin = gate_targets[key]
        require(set(pin) == {"id","table","revision","sha256","record_sha256"},
                "Unversioned historical decision: obtain a fresh gate review for this material")
        fields = ("id","sha256","table") if row["status"] == "APPROVED" and patch["status"] == "LOCKED" else tuple(pin)
        require(all(checked[key].get(k) == pin[k] for k in fields if k in pin),
                "Human gate decision covers a different material version")
        if table == "Artifact Registry":
            require(approval["gate_revision"] == gate["revision"], "Recorded approval belongs to an earlier gate version")


def bind_reviews(snapshot, intent, reviews):
    from creative_intent import TOPIC, apply_to_review, target_intent

    workflow = {r["id"]: r for r in snapshot["tables"]["Workflow"]}
    assets = {r["id"]:(t,r) for t in PRODUCTION_TABLES for r in snapshot["tables"][t]}
    gate_changes, direct = {}, set()
    for change in intent["changes"]:
        if change["values"].get("status") not in APPROVED:
            continue
        key, table = change["id"], change["table"]
        if table in PRODUCTION_TABLES:
            require(key in assets and assets[key][0] == table, "Save a draft before approving an asset")
            direct.add(key)
        if table == "Workflow":
            require(key in workflow, "Create the workflow before approving it")
            if workflow[key]["gate_id"] in CREATIVE_GATES:
                gate_changes[key] = change
    if not gate_changes and not direct:
        return intent
    prior_decisions = {row['id']:row for row in snapshot['tables']['Decisions']}
    require(not any(c['table']=='Decisions' and
                    {**prior_decisions.get(c['id'],{}),**c['values']}.get('topic')==TOPIC for c in intent['changes']),
            'Record the new creative intent before reviewing or approving related material')
    require(all(c["table"] not in PRODUCTION_TABLES or set(c["values"]) <=
                {"status","technical_review_id","artistic_review_id","approval_id"}
                for c in intent["changes"]), "Save content changes before reviewing and approving")
    require(len(gate_changes) <= 1, "Approve one workflow gate at a time")
    require(reviews is not None, "Current reviews required for creative approvals")
    reviews = reviews if isinstance(reviews, list) else [reviews]
    required_targets = set(direct)
    gate = None
    declared = {}
    if gate_changes:
        gate_id, change = next(iter(gate_changes.items()))
        gate = workflow[gate_id]
        require(change["values"].get("deliverable_ref", gate["deliverable_ref"]) == gate["deliverable_ref"],
                "Declare the reviewed deliveries before approving them")
        declared = declarations(gate["deliverable_ref"])
        require(direct <= set(declared), "Direct approvals must belong to the gate deliveries")
        required_targets.update(declared)
    checked = {}
    for review in reviews:
        require(isinstance(review, dict), "Review must be an object")
        result = validate_review(review)
        target = review["target"]
        key = target["id"]
        require(key in required_targets and key not in checked and key in assets,
                "Review is missing, duplicated or belongs to another delivery")
        table, row = assets[key]
        require(all(row[k] == review[k] for k in ("project_id","episode_id")), "Review scope mismatch")
        result = apply_to_review(result,target_intent(snapshot,table,row),review)
        require(result["recommendation"] == "READY_FOR_HUMAN_DECISION", "Review does not support approval")
        require(review["department"] in DEPARTMENTS.get(table,{row.get("department")}), "Review department mismatch")
        require(row["revision"] == target["revision"] and target.get("record_sha256") == fingerprint(row),
                "Reviewed row revision or contents changed")
        require(content_matches(table, row, target), "Reviewed material hash does not match the declared delivery")
        if gate:
            require(all(row[k] == gate[k] for k in ("project_id","episode_id")), "Gate delivery scope mismatch")
            cross_gate = gate["gate_id"] in {"G13","G14"} and review["context"].get("review_gate_id") == gate["gate_id"]
            require(row["gate_id"] == gate["gate_id"] or cross_gate, "Review gate mismatch")
        checked[key] = {"id":key,"table":table,"revision":row["revision"],
                        "sha256":target["sha256"],"record_sha256":target["record_sha256"]}
        require(all(checked[key].get(k) == v for k,v in declared.get(key,{}).items()), "Declared delivery pin is stale")
    require(set(checked) == required_targets, "Missing review for one or more gate deliveries")
    check_direct_binding(snapshot,intent,assets,direct,checked,gate)
    bound_intent = copy.deepcopy(intent)
    if gate:
        manifest = canonical({"format":"cpe-deliveries-1","targets":[checked[key] for key in declared]})
        for change in bound_intent["changes"]:
            if change["table"] == "Workflow" and change["id"] == gate["id"]:
                change["values"]["deliverable_ref"] = manifest
    return bound_intent


# Indices are the stable, one-based positions validated against gates.json.
# Other criteria may legitimately be verified by a plan, e.g. G13 sound/color plan.
INSPECTION_CRITERIA = {"G7": {3}, "G8": {4}, "G9": {3}, "G11": {1,2,3},
                       "G12": {1,2}, "G13": {3}, "G14": {1,2,3,4}}


def verify_observations(snapshot, changes, message_ref):
    """Apply stricter criteria to new approvals/edited closed checklists, not old history."""
    touched = set()
    for change in changes:
        if change["table"] == "Workflow":
            touched.add(change["id"])
        elif change["table"] == "Checklists":
            touched.add(change["after"]["workflow_id"])
    for gate in snapshot["tables"]["Workflow"]:
        if gate["id"] not in touched or gate["status"] not in APPROVED:
            continue
        checks = [c for c in snapshot["tables"]["Checklists"]
                  if c["workflow_id"] == gate["id"] and
                  c["item_index"] in INSPECTION_CRITERIA.get(gate["gate_id"], set())]
        for check in checks:
            require(check["checked"] and check["observed_or_planned"] == "observed",
                    "Observation required for " + gate["gate_id"] + ": " + check["criterion"])
        if gate["gate_id"] != "G14":
            continue
        pins = declarations(gate["deliverable_ref"])
        approvals = [a for a in snapshot["tables"]["Approvals"] if a["workflow_id"] == gate["id"]
                     and a["gate_revision"] == gate["revision"] and a["status"] == "RECORDED"]
        require(any(a["user_message_ref"] == message_ref for a in approvals),
                "QC approval must reference the received authorization for this version")
        covered = set()
        for check in checks:
            try:
                evidence = json.loads(check["evidence"])
            except ValueError as e:
                raise StateError("QC evidence must identify observation, source and reviewed versions") from e
            require(isinstance(evidence, dict) and all(isinstance(evidence.get(k), str)
                    and evidence[k].strip() for k in ("observation","evidence_ref")),
                    "QC evidence needs an observation and an accessible evidence reference")
            targets = evidence.get("targets")
            require(isinstance(targets, list) and targets, "QC observation must identify the reviewed material")
            for target in targets:
                require(isinstance(target, dict) and isinstance(target.get("id"), str)
                        and target["id"] in pins, "Unknown QC evidence target")
                current = pins[target["id"]]
                require(all(k in target and k in current and target[k] == current[k]
                            for k in ("revision","sha256")), "QC observation belongs to another version")
                covered.add(target["id"])
        require(covered == set(pins), "One or more QC deliveries have no scoped observation")
