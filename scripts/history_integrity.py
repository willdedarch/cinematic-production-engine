"""Validate native journal copies. No I/O or remote lock is implied."""
from collections import defaultdict
import json

from journal_codec import decode_event
from shared_state import Conflict, StateError, fingerprint, require, timestamp


def ensure_preserved(plan, rows):
    # 1.1 plans already keep the journal at plan creation inside their candidate.
    baseline = plan.get("history_baseline")
    if baseline is None:
        baseline = {r["id"]: fingerprint(r) for r in plan["candidate"]["tables"]["Revision History"]
                    if r["op_id"] != plan["op_id"]}
    current = {r["id"]: r for r in rows}
    for key, checksum in baseline.items():
        if key not in current or fingerprint(current[key]) != checksum:
            raise Conflict("Known journal row missing or modified: " + key)


def event_identity(row):
    return row["actor"], row["authorization_ref"], json.loads(row["guards_json"])

def pending_new_scope(snapshot, op):
    """PREPARED can reserve a new episode before its project/episode rows exist."""
    rows=[r for r in snapshot['tables']['Revision History'] if r['op_id']==op]
    require(rows and all(r['event']=='PREPARED' for r in rows),'Missing scope after an operation completed')
    changes=decode_event(rows)
    check_event_series(changes,rows,snapshot['read_at'])
    require(all(event_identity(r)==event_identity(rows[0]) for r in rows),'Inconsistent prepared event')
    anchors={}
    for c in changes:
        if c['table'] in {'Projects','Episodes'} and c['before'] is None:
            r=c['after'];field='project_id' if c['table']=='Projects' else 'episode_id'
            require(r['id']==c['id']==r[field] and r['last_op_id']==op and r['revision']==1 and r['updated_by']==rows[0]['actor'],'Invalid new scope preimage')
            anchors[c['table'],r['id']]=r
    return anchors


def check_event_series(changes, events, read_at):
    anchors = {(c['after']['project_id'], c['after']['episode_id'], c['after']['is_test']) for c in changes}
    # Both the original project-wide journal and a scoped episode journal are valid.
    anchors.update((project, '', test) for project, _, test in tuple(anchors))
    scopes = {(r['project_id'],r['episode_id'],r['is_test']) for r in events}
    require(scopes <= anchors, 'Journal scope does not cover the operation')
    require(len(scopes) == 1, 'Journal event parts must use the same project and episode')
    require(all(r['last_op_id'] == r['op_id'] and r['updated_by'] == r['actor'] for r in events),
            'Journal row belongs to a different operation or executor')
    observed = timestamp(read_at)
    prepared = [timestamp(r['updated_at']) for r in events if r['event']=='PREPARED']
    confirmed = [timestamp(r['updated_at']) for r in events if r['event']=='CONFIRMED']
    require(all(value <= observed for value in prepared + confirmed), 'Journal event postdates its readback')
    if confirmed:
        require(prepared and max(prepared) <= min(confirmed), 'Confirmation must follow every preparation part')


def ensure_no_pending_overlap(plan, rows, read_at):
    targets = {(c["table"], c["id"]) for c in plan["changes"]}
    operations = defaultdict(list)
    for row in rows:
        if row["op_id"] != plan["op_id"]:
            operations[row["op_id"]].append(row)
    for operation, entries in operations.items():
        prepared = [r for r in entries if r["event"] == "PREPARED"]
        if not prepared:
            continue
        from reconciliation import is_closed
        if is_closed(entries):
            continue
        try:
            changes = decode_event(prepared)
            written = {(c["table"], c["id"]) for c in changes}
        except (TypeError, KeyError, ValueError) as error:
            raise Conflict("Incomplete preparation needs reconciliation: " + operation) from error
        if not targets.intersection(written):
            continue
        confirmed = [r for r in entries if r["event"] == "CONFIRMED"]
        unresolved = any(r["event"] in {"CONFLICT", "INCOMPLETE"} for r in entries)
        if confirmed and not unresolved:
            try:
                check_event_series(changes, prepared + confirmed, read_at)
                closed = (decode_event(confirmed) == changes and
                          all(event_identity(r) == event_identity(prepared[0])
                              for r in prepared + confirmed))
            except (TypeError, KeyError, ValueError):
                closed = False
            if closed:
                continue
        raise Conflict("Unresolved operation on the same material: " + operation)


def own_event(plan, rows, kind):
    selected = [r for r in rows if r["op_id"] == plan["op_id"] and r["event"] == kind]
    require(bool(selected), "Missing journal " + kind)
    digest = {"algorithm": "sha256-canonical", "digest": fingerprint(plan["guards"])}
    for row in selected:
        actor, authorization, guards = event_identity(row)
        require(actor == plan["actor"] and authorization == plan["authorization_ref"],
                "Mismatched journal actor/authorization")
        require(timestamp(row["updated_at"]) >= timestamp(plan["prepared_at"]),
                "Journal event predates preparation")
        require(guards == plan["guards"] or guards == digest, "Mismatched journal guards")
    require(decode_event(selected) == plan["changes"], "Mismatched journal changes")


def verify_journal(plan, snapshot, require_prepared=False, require_confirmed=False, prewrite=False):
    rows = snapshot["tables"]["Revision History"]
    ensure_preserved(plan, rows)
    ensure_no_pending_overlap(plan, rows, snapshot['read_at'])
    ours = {r["event"] for r in rows if r["op_id"] == plan["op_id"]}
    require(not ours.intersection({"CONFLICT","INCOMPLETE"}),
            "Operation has an unresolved incident; reconcile before continuing")
    if prewrite and "CONFIRMED" in ours:
        raise Conflict("Operation already confirmed; never replay the write")
    if require_prepared or "PREPARED" in ours:
        own_event(plan, rows, "PREPARED")
    if require_confirmed or "CONFIRMED" in ours:
        own_event(plan, rows, "CONFIRMED")
    events = [r for r in rows if r['op_id'] == plan['op_id'] and r['event'] in {'PREPARED','CONFIRMED'}]
    if events:
        check_event_series(plan['changes'], events, snapshot['read_at'])
