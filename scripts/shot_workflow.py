"""Versioned shot cards, impact tracing and local handoffs for manual production."""
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, re

from shared_state import ASSETS, SCHEMA, canonical, fingerprint, index, prepare, require, validate, timestamp
from series_bible import source_link
from prompt_compiler import compile_prompt, CAT, ORDER

ROOT=Path(__file__).resolve().parents[1]
TOPIC="CPE_SHOT_LINK_V1"
RELATIONS={"reference","storyboard","take","selected_take","edit","uses","exception"}
MATERIALS = ASSETS | {"Artifact Registry"}

def check_relationship(ix, decision, data, current=False):
    require(isinstance(data,dict) and data.get("relation") in RELATIONS and decision["rationale"].strip(),
            "Invalid production relationship")
    endpoints = []
    for side in ("from","to"):
        d = data.get(side)
        require(isinstance(d,dict) and set(d)=={"id","table","revision","sha256"}
                and d["table"] in MATERIALS and isinstance(d["id"],str), "Invalid versioned shot endpoint")
        row = ix[d["table"]].get(d["id"])
        require(row and row["project_id"]==decision["project_id"] and row["is_test"]==decision["is_test"],
                "Missing or cross-project shot endpoint")
        require(type(d["revision"]) is int and 1 <= d["revision"] <= row["revision"] and
                isinstance(d["sha256"],str) and re.fullmatch("[0-9a-f]{64}",d["sha256"]), "Invalid versioned shot endpoint")
        if current or d["revision"] == row["revision"]:
            require(d==ref(d["table"],row),"Missing or stale version: "+d["id"])
        endpoints.append(row)
    left,right=endpoints
    source,target=data["from"]["table"],data["to"]["table"]
    require(left["id"]!=right["id"] and decision["episode_id"] == (right["episode_id"] or left["episode_id"]),
            "Invalid relationship or episode scope")
    relation=data["relation"]
    if relation=="reference":
        require(source=="Artifact Registry" and target=="Shot List" and (not current or left["kind"]=="REFERENCE")
                and isinstance(data.get("role"),str) and data["role"].strip(),"Identify the shot reference and its input role")
        position=data.get("position")
        require(position is None or type(position) is int and position>=1,"Reference position must be positive")
    elif relation in {"take","selected_take"}:
        require(source=="Shot List" and target=="Artifact Registry" and left["episode_id"]==right["episode_id"]
                and (not current or right["kind"]!="REFERENCE"),"Take must be registered media for this episode")
    elif relation=="exception":
        require(source==target=="Shot List" and left["episode_id"]==right["episode_id"] and data.get("field")
                and (not current or left["scene_beat"]==right["scene_beat"] and left["order"]<right["order"]),
                "Continuity exception must identify a field between ordered shots in the same scene")

def new_link(snapshot, decision, message):
    require(decision["user_message_ref"]==message,"Shot relationship must cite its current authorization")
    data=json.loads(decision["choice"])
    ix=index(snapshot)
    check_relationship(ix,decision,data,current=True)
    if data["relation"]=="selected_take":
        linked = [json.loads(d["choice"]) for d in ix["Decisions"].values() if d["topic"]==TOPIC and d["status"]=="RECORDED"]
        require(any(v["relation"]=="take" and v["from"]==data["from"] and v["to"]==data["to"] for v in linked),
                "Register this exact take against this shot before selecting it")
def validate_shot_links(snapshot):
    ix=index(snapshot)
    for decision in snapshot["tables"]["Decisions"]:
        if decision["topic"]!=TOPIC:continue
        check_relationship(ix,decision,json.loads(decision["choice"]))
    return True
def ref(table,row):
    return {"table":table,"id":row["id"],"revision":row["revision"],"sha256":fingerprint(row)}
def resolve(ix,descriptor):
    row=ix.get(descriptor["table"],{}).get(descriptor["id"])
    require(row is not None and descriptor==ref(descriptor["table"],row),"Missing or stale version: "+descriptor["id"])
    return row
def stamp():
    return datetime.now(timezone.utc).isoformat()
def digest_file(path):
    with path.open("rb") as stream:return hashlib.file_digest(stream,"sha256").hexdigest()
def link_change(snapshot,spec,source,target):
    ix=index(snapshot)
    left,right=resolve(ix,source),resolve(ix,target)
    require(left["project_id"]==right["project_id"] and left["is_test"]==right["is_test"],"Cross-project link")
    relation=spec["relation"]
    require(relation in RELATIONS and source["id"]!=target["id"],"Invalid shot relationship")
    require(relation!="reference" or (source["table"]=="Artifact Registry" and target["table"]=="Shot List" and left["kind"]=="REFERENCE"),"Select a registered reference for the shot")
    if relation in {"take","selected_take"}:
        require(source["table"]=="Shot List" and target["table"]=="Artifact Registry" and left["episode_id"]==right["episode_id"],"Take requires a shot and a registered asset from its episode")
    details={"from":source,"to":target,"relation":relation,"field":spec.get("field",""),"role":spec.get("role","")}
    if relation=="reference" and "position" in spec:details["position"]=spec["position"]
    require(spec.get("reason","").strip(),"Explain the link or the continuity exception")
    values={"project_id":right["project_id"],"episode_id":right["episode_id"] or left["episode_id"],"is_test":left["is_test"],
            "gate_id":"G10","topic":TOPIC,"choice":canonical(details),"rationale":spec["reason"],
            "user_message_ref":spec["authorization"]["user_message_ref"],"status":"RECORDED"}
    return {"table":"Decisions","id":spec["decision_id"],"expected_revision":None,"values":values}
def edges(snapshot,shot):
    result=[]
    ix=index(snapshot)
    def edge(a,b,kind,field="",source=None,role=""):
        result.append({"from":a,"to":b,"relation":kind,"field":field,"decision":source,"role":role})
    for row in snapshot["tables"]["Shot List"]:
        if row["project_id"]!=shot["project_id"]:continue
        for table,keys in [("Locations",row["location_id"]),("Characters",row["character_ids"]),("Props",row["prop_ids"])]:
            for key in filter(None,keys.split(",")):
                edge(ref(table,ix[table][key]),ref("Shot List",row),"uses")
    for p in snapshot["tables"]["Prompts"]:
        if p["project_id"]==shot["project_id"]:
            dest=ix[p["target_table"]][p["target_id"]]
            edge(ref(p["target_table"],dest),ref("Prompts",p),"prompt")
    for d in snapshot["tables"]["Decisions"]:
        if d["project_id"]!=shot["project_id"] or d["topic"]!=TOPIC or d["status"]!="RECORDED":continue
        data=json.loads(d["choice"])
        edge(data["from"],data["to"],data["relation"],data.get("field",""),source_link(snapshot,d),data.get("role",""))
        if "position" in data:result[-1]["position"]=data["position"]
    return result
def state(row):
    raw=row["start_end_state"]
    try:value=json.loads(raw)
    except (TypeError,ValueError):return {"text":raw}
    return value if isinstance(value,dict) else {"text":raw}
def card(snapshot,shot_id):
    validate(snapshot)
    ix=index(snapshot);row=ix["Shot List"].get(shot_id)
    require(row is not None,"Shot not found")
    links=[x for x in edges(snapshot,row) if shot_id in (x["from"]["id"],x["to"]["id"])]
    for link in links:
        link["stale"]=any(ix.get(d["table"],{}).get(d["id"]) is None or ref(d["table"],ix[d["table"]][d["id"]])!=d for d in (link["from"],link["to"]))
    sequence=sorted((p for p in snapshot["tables"]["Shot List"] if p["episode_id"]==row["episode_id"] and p["scene_beat"]==row["scene_beat"] and p["status"]!="ARCHIVED"),key=lambda p:(p["order"],p["id"]))
    previous=[p for p in sequence if p["order"]<row["order"]]
    incoming=state(row).get("in",{})
    warnings=[]
    if previous:
        outgoing=state(previous[-1]).get("out",{})
        for key in sorted(set(incoming)&set(outgoing)):
            if incoming[key]!=outgoing[key]:
                exceptions=[e["decision"] for e in links if e["relation"]=="exception" and not e["stale"] and e["field"]==key and e["from"]["id"]==previous[-1]["id"] and e["to"]["id"]==shot_id]
                warnings.append({"field":key,"previous_shot":previous[-1]["id"],"before":outgoing[key],"after":incoming[key],
                                 "status":"JUSTIFIED" if exceptions else "REVIEW_REQUIRED","decisions":exceptions})
    def order_decision(d):return timestamp(ix["Decisions"][d["id"]]["updated_at"]),d["id"]
    latest=sorted((l["decision"] for l in links if l["decision"]),key=order_decision)
    selected=sorted((l for l in links if l["relation"]=="selected_take"),key=lambda l:order_decision(l["decision"]))
    return {"shot":ref("Shot List",row),"beat":row["scene_beat"],"order":row["order"],"duration_s":row["duration_s"],"intention":row["purpose"],
            "action":row["action"],"camera":row["camera_blocking"],"sound":row["sound_edit"],"states":state(row),"links":links,
            "selected_take":selected[-1]["to"] if selected and not selected[-1]["stale"] else None,
            "last_decision":latest[-1] if latest else None,"continuity_review":warnings}
def impact(snapshot,shot_id,field,*,current_links_only=False):
    ix=index(snapshot);origin=ix["Shot List"].get(shot_id)
    require(origin,"Unknown shot")
    graph=defaultdict(list)
    for e in edges(snapshot,origin):
        if current_links_only and any(ref(v["table"],ix[v["table"]][v["id"]])!=v for v in (e["from"],e["to"])):
            continue
        if e["relation"]!="exception" and (not field or not e["field"] or field==e["field"]):
            graph[e["from"]["id"]].append(e)
    visited={shot_id};queue=deque([shot_id]);affected=[]
    while queue:
        key=queue.popleft()
        for edge in graph[key]:
            dest=edge["to"];uid=dest["id"]
            if uid in visited:continue
            visited.add(uid);queue.append(uid)
            row=ix.get(dest["table"],{}).get(uid)
            affected.append({"linked_version":dest,"current":ref(dest["table"],row) if row else None,
                             "via":key,"relationship":edge["relation"],"status":row.get("status") if row else "MISSING"})
    return {"source":ref("Shot List",origin),"field":field,"affected":affected,"implicit_unlinked_dependencies":"Ask director to confirm undeclared dependencies"}

def handoff(snapshot,spec):
    sheet=card(snapshot,spec["shot_id"])
    require(not any(w["status"]=="REVIEW_REQUIRED" for w in sheet["continuity_review"]),"Resolve or justify the continuity change first")
    ix=index(snapshot);shot=resolve(ix,sheet["shot"])
    require(spec["model_id"] in CAT["models"],"Model not in the verified catalog")
    require(CAT["models"][spec["model_id"]]["output_type"]=="video","Shot handoff expects a video adapter")
    fields={"initial_state":canonical(sheet["states"].get("in",sheet["states"])),"action":sheet["action"],"camera":sheet["camera"],
            "sound":sheet["sound"],"protected":canonical(sheet["states"].get("out",{})),"performance":sheet["intention"]}
    references=[]
    latest={}
    for link in sheet["links"]:
        if link["relation"]=="reference" and link["to"]["id"]==shot["id"]:
            decision=ix["Decisions"][link["decision"]["id"]]
            key=link["from"]["id"]
            order=(timestamp(decision["updated_at"]),decision["id"])
            if key not in latest or order>latest[key][0]:latest[key]=(order,link)
    for _,link in latest.values():
        require(not link["stale"],"Reconfirm the reference after version change")
        record=resolve(ix,link["from"]);uri=Path(record["uri"])
        path=uri if uri.is_absolute() else ROOT/uri
        require(path.is_file() and digest_file(path)==record["sha256"],"Local reference bytes differ or are missing")
        require(record["rights"].strip(),"Reference rights missing")
        references.append({"id":record["id"],"revision":record["revision"],"sha256":record["sha256"],"uri":record["uri"],
                           "role":link["role"],"position":link.get("position"),"rights_confirmed":True,"rights":record["rights"]})
    model=spec["model_id"];params=dict(spec.get("parameters",{}))
    roles=list(dict.fromkeys(r for m in CAT["models"][model]["medias"] for r in m.get("roles",[])))
    by_role=defaultdict(list)
    for r in references:
        require(r["role"] in roles,"Unsupported reference role: "+r["role"])
        by_role[r["role"]].append(r)
    explicit=spec.get("reference_order",{})
    require(isinstance(explicit,dict) and set(explicit)<=set(by_role),"Unknown reference ordering role")
    references=[]
    for role in roles:
        items=by_role[role]
        if role in explicit:
            ids=explicit[role]
            require(isinstance(ids,list) and all(isinstance(i,str) for i in ids) and len(ids)==len(items)
                    and set(ids)=={r["id"] for r in items},"Order must list every reference ID in its role exactly once")
            items.sort(key=lambda r:ids.index(r["id"]))
        elif len(items)>1:
            positions=[r["position"] for r in items]
            require(None not in positions and len(set(positions))==len(items),"Multiple references in one role require explicit order")
            items.sort(key=lambda r:r["position"])
        for n,r in enumerate(items,1):r["position"]=n
        references.extend(items)
    if any(p["name"]=="duration" for p in CAT["models"][model]["parameters"]):
        require("duration" not in params or params["duration"]==shot["duration_s"],"Duration differs from shot")
        params["duration"]=shot["duration_s"]
    compiled=compile_prompt({"model_id":model,"aspect_ratio":ix["Episodes"][shot["episode_id"]]["aspect_ratio"],
                             "intent":{k:v for k,v in fields.items() if k in ORDER[model]},"parameters":params,"references":references})
    return {"shot":sheet["shot"],"delivery":compiled,"attachment_order":[{"id":r["id"],"field":r["role"],"position":r["position"],"file":r["uri"],"revision":r["revision"],"sha256":r["sha256"]} for r in references],
            "return_checklist":["Identificar plano, versão e origem","Conferir duração e ação no take","Registrar direitos e revisão técnica/artística"],"execution":"MANUAL"}

def repair_changes(snapshot, spec):
    """Constrain a repair to the reviewed impact, versions, fields and episode."""
    ix=index(snapshot)
    signed=spec.get("impact")
    require(isinstance(signed,dict) and isinstance(spec.get("field"),str) and spec["field"].strip(),
            "Provide the reviewed shot-impact result and its field")
    scope=impact(snapshot,spec["shot_id"],spec["field"])
    require(signed==scope,"Impact changed: inspect current shot and dependencies before authorizing")
    active=impact(snapshot,spec["shot_id"],spec["field"],current_links_only=True)
    allowed={scope["source"]["id"]}|{r["current"]["id"] for r in active["affected"]}
    origin=ix["Shot List"][spec["shot_id"]]
    changes=spec.get("changes")
    require(isinstance(changes,list) and changes,"Provide proposed changes and authorized fields")
    result=[]
    for ch in changes:
        table=ch["table"]
        require(table in MATERIALS,"Shot repairs concern production materials")
        values=ch["values"]
        existing=ix[table].get(ch["id"])
        row=existing or ix[table].get(values.get("supersedes_id"))
        require(row and row["id"] in allowed and row["episode_id"]==origin["episode_id"],
                "Repair requires a current relationship and a target in this episode")
        require(not existing or row["status"] not in {"APPROVED","LOCKED"},"Create a successor for the protected version")
        require(spec.get("pins",{}).get(row["id"])==ref(table,row),"Recheck the exact target or predecessor version")
        if not existing:
            require(all(values.get(k)==row[k] for k in ("project_id","episode_id","is_test"))
                    and values.get("status") in {"DRAFT","REVIEW_REQUIRED"}
                    and values.get("version")!=row["version"],"New version must identify its predecessor, episode and draft status")
        structural={"supersedes_id","version","project_id","episode_id","is_test","status"}
        changed={k for k,v in values.items() if k not in structural and row.get(k)!=v}
        require(changed and set(spec.get("fields",{}).get(ch["id"],[]))==changed,
                "Identify each content field authorized on each changed record")
        require(values.get("status") not in {"APPROVED","LOCKED","ARCHIVED"},"Review repaired content before approval or archiving")
        if existing:
            require(not set(values).intersection(structural-{"status"}),"Preserve current record identity and lineage")
        else:
            # All fields not explicitly edited inherit the exact predecessor, including scope.
            inherited={k:row[k] for k in SCHEMA["tables"][table]["columns"]
                       if k not in {"id","revision","updated_at","updated_by","last_op_id"}}
            values={**inherited,**values}
        if row["id"]==origin["id"]:
            field=spec["field"]
            if field in origin:
                require(changed=={field},"Root repair exceeds the authorized shot field")
            else:
                before=state(row)
                after=state({**row,**values})
                require(changed=={"start_end_state"} and (field in before.get("in",{}) or field in before.get("out",{}))
                        and set(before)==set(after) and set(before)<={"in","out"},"Root repair must concern the declared continuity field")
                for side in before:
                    require(isinstance(before[side],dict) and isinstance(after[side],dict) and
                            {k:v for k,v in before[side].items() if k!=field}=={k:v for k,v in after[side].items() if k!=field},
                            "Continuity repair changes another protected field")
        result.append({**ch,"values":values})
    return result

def dispatch(cmd,snapshot,spec,outdir):
    validate(snapshot)
    ix=index(snapshot)
    if cmd=="storyboard":
        rows=[r for r in snapshot["tables"]["Shot List"] if r["episode_id"]==spec["episode_id"] and r["scene_beat"]==spec["scene_beat"] and r["status"]!="ARCHIVED"]
        require(rows,"No shots in this scene")
        return {"cards":[card(snapshot,r["id"]) for r in sorted(rows,key=lambda r:(r["order"],r["id"]))]}
    if cmd=="shot-card":return card(snapshot,spec["shot_id"])
    if cmd=="shot-impact":return impact(snapshot,spec["shot_id"],spec.get("field",""))
    if cmd=="shot-handoff":return handoff(snapshot,spec)
    if cmd=="shot-link":changes=[link_change(snapshot,spec,spec["from"],spec["to"])]
    if cmd=="shot-repair":
        changes=repair_changes(snapshot,spec)
    if cmd=="shot-import":
        from harness_runtime import import_asset
        shot=resolve(ix,spec["shot"])
        require(spec["shot"]["table"]=="Shot List","Import needs a current shot")
        asset=import_asset(spec["path"],spec.get("kind","FINAL_ASSET"),spec["asset_id"],1,spec["origin"],spec["rights_confirmed"])
        entry={"table":"Artifact Registry","id":asset["id"],"expected_revision":None,"values":{
            "project_id":shot["project_id"],"episode_id":shot["episode_id"],"is_test":shot["is_test"],"gate_id":"G12","kind":asset["kind"],
            "department":"editing","version":1,"uri":asset["uri"],"sha256":asset["sha256"],"origin":spec["origin"],"rights":spec["rights"],"status":"REVIEW_REQUIRED"}}
        at=stamp()
        draft=prepare(snapshot,{**spec["authorization"],"at":at,"changes":[entry]})
        dest=ref("Artifact Registry",index(draft["candidate"])["Artifact Registry"][asset["id"]])
        link=link_change(draft["candidate"],{**spec,"relation":"take"},spec["shot"],dest)
        return prepare(snapshot,{**spec["authorization"],"at":at,"changes":[entry,link]})
    return prepare(snapshot,{**spec["authorization"],"at":stamp(),"changes":changes})

