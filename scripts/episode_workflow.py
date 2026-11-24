"""Plan the first or following episode with stable project-level identity."""
import uuid
from datetime import datetime, timezone

from series_bible import handoff
from shared_state import GATES, prepare, require, validate

def initialize_episode(snapshot, brief, authorization):
    validate(snapshot)
    title = brief.get("episode_title", "")
    duration = brief.get("target_seconds")
    require(isinstance(title, str) and title.strip(), "Episode title required")
    require(type(duration) in (int, float) and duration > 0, "Positive target duration required")
    pid = brief.get("project_id") or ("P-" + uuid.uuid4().hex[:12])
    project = next((p for p in snapshot["tables"]["Projects"] if p["id"] == pid), None)
    previous = sorted((e for e in snapshot["tables"]["Episodes"] if e["project_id"] == pid), key=lambda e:e["episode_number"])
    if project:
        require(brief.get("new_episode") is True or brief.get("episode_id") or brief.get("episode_number"), "Specify a new episode or resume the existing one")
        require(project["status"] == "ACTIVE", "Project is archived")
        require("is_test" not in brief or brief["is_test"] is project["is_test"], "Series test scope differs from the request")
    else:
        require(not brief.get("new_episode"), "Create the series before adding an episode")
        require(isinstance(brief.get("project_name"), str) and brief["project_name"].strip(), "Project name required")
    numbers = [e["episode_number"] for e in previous]
    require(len(set(numbers)) == len(numbers), "Reconcile duplicate episode numbers")
    next_number = max(numbers,default=0)+1
    requested=brief.get("episode_number",next_number)
    require(type(requested) is int and requested == next_number, f"Next available episode number is {next_number}")
    eid = brief.get("episode_id") or f"{pid}-EP{next_number}"
    test = project["is_test"] if project else brief.get("is_test",False)
    require(type(test) is bool, "Invalid test marker")
    if project and test:
        require(brief.get("include_test") is True, "Explicit test scope required")
    changes = []
    def add(table, uid, **values):
        values.update(project_id=pid,episode_id="" if table=="Projects" else eid,is_test=test)
        changes.append({"table":table,"id":uid,"expected_revision":None,"values":values})
    if not project:
        add("Projects",pid,name=brief["project_name"],mode=brief.get("mode","guided"),credits_allowed=0,generation_mode="manual",status="ACTIVE")
    defaults = previous[-1] if previous else {}
    add("Episodes",eid,title=title,episode_number=next_number,target_seconds=duration,aspect_ratio=brief.get("aspect_ratio",defaults.get("aspect_ratio","16:9")),
        genre=brief.get("genre",defaults.get("genre","drama")),status="ACTIVE",continuity_ref="")
    for gate in GATES:
        wid = f"{eid}-{gate['id']}"
        add("Workflow",wid,gate_id=gate["id"],name=gate["name"],status="PENDING",depends_on=",".join(gate["depends"]),skippable=gate["skippable"])
        for i, criterion in enumerate(gate["checks"],1):
            add("Checklists",f"{wid}-C{i}",workflow_id=wid,gate_id=gate["id"],item_index=i,criterion=criterion,checked=False,observed_or_planned="planned")
    plan = prepare(snapshot,{**authorization,"at":datetime.now(timezone.utc).isoformat(),"changes":changes})
    plan["episode_handoff"] = handoff(plan["candidate"],pid,eid,before_episode=True)
    return plan
