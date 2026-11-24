"""Episode handoffs and decision-backed story facts on the existing Sheets schema."""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from shared_state import canonical, fingerprint, prepare, require, validate

TOPIC = "CPE_CANON_V1"
KINDS = {"character_knowledge", "audience_knowledge", "relationship", "prop", "location", "open_question"}
ROOT = Path(__file__).resolve().parents[1]

def group_key(fact):
    return fact["kind"], fact["subject"], fact["key"]

def read_fact(row):
    try:
        fact = json.loads(row["choice"])
    except (TypeError, ValueError) as error:
        raise ValueError("Unreadable story fact: " + row["id"]) from error
    require(isinstance(fact, dict) and fact.get("kind") in KINDS, "Unknown story fact category")
    for key in ("subject", "key", "value", "beat"):
        require(isinstance(fact.get(key), str) and bool(fact[key].strip()), "Missing story fact " + key)
    require(type(fact.get("sequence")) is int and fact["sequence"] > 0, "Scene sequence must be positive")
    require(isinstance(fact.get("previous_decision_id", ""), str), "Invalid previous decision")
    require(fact["kind"] != "audience_knowledge" or fact["subject"] == "AUDIENCE", "Audience facts use AUDIENCE")
    return fact

def validate_canon_ledger(snapshot):
    episodes = {r["id"]: r for r in snapshot["tables"]["Episodes"]}
    episode_positions = {(ep['project_id'], ep['episode_number']) for ep in episodes.values()}
    require(len(episode_positions) == len(episodes), 'Duplicate episode number in the same project; reconcile the chronology')
    groups = defaultdict(list)
    for row in snapshot["tables"]["Decisions"]:
        if row["topic"] != TOPIC:
            continue
        require(row["episode_id"] in episodes, "Series fact requires an episode")
        fact = read_fact(row)
        if row["status"] == "RECORDED":
            require(bool(row["rationale"].strip()), "Recorded fact requires decision rationale")
            groups[(row["project_id"], *group_key(fact))].append(
                (episodes[row["episode_id"]]["episode_number"], fact["sequence"], row["id"], fact))
    for items in groups.values():
        previous = ""
        positions = set()
        for episode_no, sequence, row_id, fact in sorted(items):
            require((episode_no, sequence) not in positions, "Ambiguous fact order within beat")
            require(fact.get("previous_decision_id", "") == previous, "Changed canon must name its actual predecessor")
            positions.add((episode_no, sequence))
            previous = row_id
    return True

def source_link(snapshot, row):
    from local_binding import load_binding
    binding = load_binding()
    source = {"table": "Decisions", "id": row["id"], "revision": row["revision"],
              "record_sha256": fingerprint(row), "message": row["user_message_ref"], "reason": row["rationale"]}
    if binding["spreadsheet_id"] == snapshot["spreadsheet_id"]:
        base = f'https://docs.google.com/spreadsheets/d/{quote(binding["spreadsheet_id"], safe="")}/edit#gid={binding["sheet_ids"]["Decisions"]}'
        position = snapshot.get("source_rows", {}).get("Decisions", {}).get(row["id"])
        source["sheet_url"] = base + (f"&range=A{position}" if type(position) is int and position >= 2 else "")
    return source

def handoff(snapshot, project_id, episode_id, *, before_episode=False, through_sequence=None):
    validate(snapshot)
    episodes = {r["id"]: r for r in snapshot["tables"]["Episodes"] if r["project_id"] == project_id}
    require(episode_id in episodes, "Episode not in project")
    number = episodes[episode_id]["episode_number"]
    require(through_sequence is None or type(through_sequence) is int and through_sequence >= 0, "Invalid scene position")
    ordered, drafts, legacy = [], [], []
    for row in snapshot["tables"]["Decisions"]:
        if row["project_id"] != project_id or row["episode_id"] not in episodes:
            continue
        ep_no = episodes[row["episode_id"]]["episode_number"]
        if ep_no > number or (before_episode and ep_no == number):
            continue
        if row['topic'] in {'CPE_SHOT_LINK_V1','CPE_DESK_PROPOSAL_V1','CPE_DESK_RESULT_V1'}:
            continue  # Technical media links belong to the shot card, not the story ledger.
        if row["topic"] != TOPIC:
            # Unpositioned legacy decisions cannot be placed before a specific scene
            # within this episode. Earlier episodes have a known relative order.
            if row["status"] == "RECORDED" and (through_sequence is None or ep_no < number):
                legacy.append({"topic":row["topic"], "choice":row["choice"], "source":source_link(snapshot, row)})
            continue
        f = read_fact(row)
        if ep_no == number and through_sequence is not None and f["sequence"] > through_sequence:
            continue
        item = {**f, "episode_id":row["episode_id"], "episode_number":ep_no, "source":source_link(snapshot,row)}
        if row["status"] == "RECORDED":
            ordered.append(item)
        elif row["status"] == "DRAFT":
            drafts.append(item)
    latest = {}
    ordered.sort(key=lambda item: (item["episode_number"],item["sequence"],item["source"]["id"]))
    for item in ordered:
        latest[group_key(item)] = item
    groups = {k:[] for k in sorted(KINDS)}
    for item in latest.values():
        groups[item["kind"]].append(item)
    previous_assets = []
    eligible = {e["id"] for e in episodes.values() if e["episode_number"] < number}
    for table in ("Characters","Props","Locations"):
        for asset in snapshot["tables"][table]:
            if asset["project_id"] == project_id and asset["episode_id"] in eligible and asset["status"] in {"APPROVED","LOCKED"}:
                previous_assets.append({"table":table,"id":asset["id"],"revision":asset["revision"],"episode_id":asset["episode_id"]})
    return {"episode_id":episode_id,"project_id":project_id,"episode_number":number,"facts":groups,
            "timeline":ordered,"proposals":drafts,"earlier_decisions":legacy,"reusable_versions":previous_assets}

def check_assumptions(bible, assertions):
    require(isinstance(assertions,list), "Provide scene assumptions as a list")
    known = {group_key(f):f for facts in bible["facts"].values() for f in facts}
    results = []
    for a in assertions:
        require(a.get("kind") in KINDS and all(isinstance(a.get(k),str) and a[k].strip() for k in ("subject","key","value")), "Invalid scene assumption")
        fact = known.get(group_key(a))
        status = "UNKNOWN" if fact is None else "MATCH" if fact["value"] == a["value"] else "CONFLICT"
        results.append({"assertion":a,"status":status,"decision":fact["source"] if fact else None,
                        "canonical_value":fact["value"] if fact else None})
    return results

def canon_plan(snapshot, spec):
    project, episode = spec["project_id"], spec["episode_id"]
    ep = next((e for e in snapshot["tables"]["Episodes"] if e["id"] == episode and e["project_id"] == project), None)
    require(ep, "Unknown project/episode")
    changes = []
    for item in spec["entries"]:
        status = item.get("status","DRAFT")
        require(status in {"DRAFT","RECORDED"}, "Invalid canon submission status")
        values = {"project_id":project,"episode_id":episode,"gate_id":item.get("gate_id","G3"),"is_test":ep["is_test"],
                  "topic":TOPIC,"rationale":item["reason"],"choice":canonical(item["fact"]),
                  "user_message_ref":spec["authorization"]["user_message_ref"],"status":status}
        changes.append({"table":"Decisions","id":item["decision_id"],"expected_revision":None,"values":values})
    return prepare(snapshot,{**spec["authorization"],"at":datetime.now(timezone.utc).isoformat(),"changes":changes})

