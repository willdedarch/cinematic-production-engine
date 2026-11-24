"""Versioned shot cards, impact tracing and local handoffs for manual production."""
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, re, shutil, subprocess

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
    if "return_provenance" in data:
        provenance=data["return_provenance"]
        require(relation=="take" and isinstance(provenance,dict),"Return provenance needs a take relationship")
        if provenance.get("status")=="UNBOUND_LEGACY_IMPORT":
            require(set(provenance)=={"status"},"Legacy import has no return packet evidence")
        else:
            require(set(provenance)=={"status","handoff_sha256","media_sha256"}
                    and provenance["status"]=="DECLARED_RETURN_PACKET"
                    and all(isinstance(provenance[k],str) and re.fullmatch(r"[0-9a-f]{64}",provenance[k])
                            for k in ("handoff_sha256","media_sha256")),"Invalid declared return packet")
            if current or data["to"]["revision"]==right["revision"]:
                require(provenance["media_sha256"]==right["sha256"],"Declared return bytes differ from the registered asset")
    if relation=="exception":
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


def verify_return_sources(plan):
    """Recheck locally inspected bytes before attempting the state write."""
    from takes import local_media_path

    after=index(plan['candidate'])['Artifact Registry']
    for change in plan['changes']:
        decision=change['after']
        if change['table']!='Decisions' or decision['topic']!=TOPIC or decision['status']!='RECORDED':
            continue
        data=json.loads(decision['choice'])
        if data.get('return_provenance',{}).get('status')!='DECLARED_RETURN_PACKET':
            continue
        asset=after[data['to']['id']]
        require(Path(asset['uri']).is_absolute(), 'Return packet needs the inspected absolute local path')
        path=local_media_path(asset['uri'])
        require(path.is_absolute() and path.is_file() and digest_file(path)==asset['sha256'],
                'Returned take changed or is unavailable before write')


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
        require(isinstance(incoming,dict) and isinstance(outgoing,dict),"Structured continuity states must be objects")
        for key in sorted(outgoing):
            if incoming.get(key)!=outgoing[key] or key not in incoming:
                exceptions=[e["decision"] for e in links if e["relation"]=="exception" and not e["stale"] and e["field"]==key and e["from"]["id"]==previous[-1]["id"] and e["to"]["id"]==shot_id]
                warnings.append({"field":key,"previous_shot":previous[-1]["id"],"before":outgoing[key],"after":incoming.get(key),
                                 "issue":"CHANGED" if key in incoming else "MISSING_ENTRY",
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
    from creative_intent import check_shot_binding, prompt_lines, shot_intent
    from prompt_compiler import protect_intent
    from takes import local_media_path
    from return_media import contract as media_contract

    sheet=card(snapshot,spec["shot_id"])
    require(not any(w["status"]=="REVIEW_REQUIRED" for w in sheet["continuity_review"]),"Resolve or justify the continuity change first")
    ix=index(snapshot);shot=resolve(ix,sheet["shot"])
    binding = shot_intent(snapshot,shot)
    shot_action = ' '.join(event['action'] for event in binding['events']) if binding else sheet['action']
    require(spec["model_id"] in CAT["models"],"Model not in the verified catalog")
    require(CAT["models"][spec["model_id"]]["output_type"]=="video","Shot handoff expects a video adapter")
    fields={"initial_state":canonical(sheet["states"].get("in",sheet["states"])),"action":shot_action,"camera":sheet["camera"],
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
        record=resolve(ix,link["from"])
        path=local_media_path(record["uri"])
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
    prompt_spec = {
        "model_id": model, "aspect_ratio": ix["Episodes"][shot["episode_id"]]["aspect_ratio"],
        "intent": {key: value for key, value in fields.items() if key in ORDER[model]},
        "parameters": params, "references": references,
    }
    if "shot" in spec:
        require(spec["shot"] == sheet["shot"], "Shot changed since the handoff was prepared")
    plan = spec.get("cinematic_plan")
    if plan is not None:
        require(isinstance(plan, dict), "Cinematic plan must be an object")
        require(plan.get("duration_s", shot["duration_s"]) == shot["duration_s"], "Cinematic plan duration differs from shot")
        plan = {**plan, "duration_s": plan.get("duration_s", shot["duration_s"])}
        prompt_spec["cinematic_plan"] = plan
    compiled = compile_prompt(prompt_spec)
    if binding:
        check_shot_binding(binding,shot,plan)
        compiled = protect_intent(compiled,binding)
    if plan is not None:
        first_entry = plan["beats"][0].get("entry", {})
        final_exit = plan["beats"][-1].get("exit", {})
        for name, facts in (("in", first_entry), ("out", final_exit)):
            expected = sheet["states"].get(name, {})
            require(isinstance(expected, dict) and all(field in facts and facts[field] == value for field,value in expected.items()),
                    "Cinematic plan conflicts with shot " + name + " state")
    episode = ix["Episodes"][shot["episode_id"]]
    entities = []
    for table, field, columns in (
        ("Locations", "location_id", ("geo_version", "anchors", "dimensions", "light_weather", "state")),
        ("Characters", "character_ids", ("identity", "costume", "performance")),
        ("Props", "prop_ids", ("material_scale", "owner_character_id", "state")),
    ):
        for entity_id in filter(None, shot[field].split(",")):
            row = ix[table][entity_id]
            entities.append({**ref(table,row), "status":row["status"], "name":row["name"],
                             "description":{column:row[column] for column in columns if row[column]}})
    directions = compiled.get("authored_directions", "")
    packet = {
        "kind":"MANUAL_SHOT_HANDOFF", "spreadsheet_id":snapshot["spreadsheet_id"],
        "shot":sheet["shot"], "delivery":compiled,
        **({"cinematic_plan":plan} if plan is not None else {}),
        **({"creative_intent":binding} if binding else {}),
        "attachment_order":[{"id":r["id"],"field":r["role"],"position":r["position"],"file":r["uri"],"revision":r["revision"],"sha256":r["sha256"]} for r in references],
        "production_brief":{
            "project_id":shot["project_id"], "episode_id":shot["episode_id"], "is_test":shot["is_test"],
            "scene":sheet["beat"], "order":sheet["order"], "source_status":shot["status"], "entities":entities,
            "objective":sheet["intention"], "action":shot_action, "camera_and_blocking":sheet["camera"],
            "sound_and_edit":sheet["sound"], "entry_and_exit":sheet["states"],
            "continuity_review":sheet["continuity_review"], "authored_directions":directions,
            "model_neutral_prompt":"\n".join(value for value in (sheet["intention"],shot_action,sheet["camera"],sheet["sound"],directions,prompt_lines(binding)) if value),
            "protected":{"outgoing_state":sheet["states"].get("out",{}), "authored":plan.get("protected", "") if plan else ""},
            "planning_status":"BEATS_AUTHORED" if plan else "SHOT_CARD_ONLY",
            "expected_media":media_contract(sheet["duration_s"],episode["aspect_ratio"],compiled["native_parameters"],spec.get("return_requirements",{})),
            "check_technical":["Conferir duração, proporção e faixas", "Verificar a ordem e a origem das referências"],
            "repair_if_needed":["Se um gesto ficou ilegível, isolar esse beat e testar ponto de vista ou duração",
                                 "Se um estado protegido mudou, corrigir o retorno ou abrir sucessor autorizado"],
            "review_after_return":["Ler ação e mudança de estado em cada beat", "Rever atuação, espaço e som com timecode",
                                   "Conferir continuidade dos elementos protegidos e registrar reparo por trecho"],
        },
        "return_checklist":["Identificar plano, versão, origem e direitos", "Conferir duração e proporção",
                            "Registrar revisão técnica e artística"], "execution":"MANUAL",
        "execution_instructions":["Conferir o nome, modo e campos na interface do modelo escolhido",
                                  "Anexar referências na ordem registrada e executar manualmente após autorização",
                                  "Devolver a mídia com origem e direitos e manter este pacote para comparação"],
        "request":{k:spec[k] for k in ("shot_id","model_id","parameters","reference_order","cinematic_plan","return_requirements") if k in spec},
    }
    return {**packet, "handoff_sha256":fingerprint(packet)}


def compare_handoff(snapshot, packet, path, rights_confirmed):
    from media_tools import local_file, probe
    from return_media import decode,evaluate,measurements
    from takes import local_media_path

    require(rights_confirmed is True,"Confirm rights for local take inspection")
    require(isinstance(packet,dict) and packet.get("kind")=="MANUAL_SHOT_HANDOFF","A sealed shot handoff is required")
    digest = packet.get("handoff_sha256")
    require(digest==fingerprint({k:v for k,v in packet.items() if k!="handoff_sha256"}),"Handoff content changed")
    require(packet["spreadsheet_id"]==snapshot["spreadsheet_id"],"Handoff belongs to a different spreadsheet")
    current = handoff(snapshot,{**packet["request"], "shot":packet["shot"]})
    expected = current["production_brief"]["expected_media"]
    prior_media = packet["production_brief"]["expected_media"]
    if set(prior_media)=={"duration_s","aspect_ratio"} and "return_requirements" not in packet["request"]:
        # v1.5 packets had only these fields. Compare against their exact shape,
        # retaining the full current contract for technical evaluation.
        current["production_brief"]["expected_media"] = {
            "duration_s":expected["duration_s"], "aspect_ratio":current["delivery"]["aspect_ratio"],
        }
        current["handoff_sha256"] = fingerprint({k:v for k,v in current.items() if k!="handoff_sha256"})
    require(current==packet,"References, shot context or adapter changed since export")
    source = local_file(local_media_path(path))
    result = {
        "kind":"LOCAL_SHOT_RETURN_REVIEW", "handoff_sha256":digest, "shot":packet["shot"],
        "media_sha256":digest_file(source), "expected":expected,
        "artistic_review":"PENDING", "approved":False, "saved":False,
        "review_after_return":packet["production_brief"]["review_after_return"],
        "review_beats":[{k:b[k] for k in ("id","start_s","end_s","action")} for b in packet.get("cinematic_plan",{}).get("beats",[])],
    }
    metadata = {}
    unavailable = not shutil.which("ffprobe")
    integrity = ('UNKNOWN','FFprobe não disponível. A mídia precisa de revisão manual.')
    if not unavailable:
        try:
            metadata = probe(source)
        except RuntimeError as exc:
            tool_error = str(exc).casefold()
            unavailable_errors = ('permission denied','operation not permitted','resource temporarily unavailable','input/output error')
            if tool_error.startswith('local tool failed:') and not any(e in tool_error for e in unavailable_errors):
                integrity = ('FAIL','FFprobe não conseguiu ler um contêiner válido.')
            else:
                integrity = ('UNKNOWN','Não foi possível iniciar a inspeção com FFprobe.')
        except (OSError,ValueError,subprocess.TimeoutExpired):
            integrity = ('UNKNOWN','Metadados indisponíveis ou incompletos no ambiente local.')
    observed,indexes,container_duration = measurements(metadata)
    if metadata:
        require(metadata["source_sha256"]==result["media_sha256"],"Take changed during inspection")
        durations = [d for d in (observed['duration_s'],container_duration) if d is not None]
        integrity = decode(source,indexes,max(durations,default=None))
    require(digest_file(source)==result['media_sha256'],"Take changed during inspection")
    details = evaluate(expected,observed,integrity)
    required = {check['status'] for check in details.values() if check['required']}
    status = 'UNAVAILABLE' if unavailable else 'MISMATCH' if 'FAIL' in required else \
        'INCOMPLETE' if required-{'PASS'} else 'SPEC_CHECKED'
    legacy = {'media_type':'video','duration_s':'duration','aspect_ratio':'aspect_ratio'}
    binary = {'PASS':True,'FAIL':False}
    matches = {legacy.get(k,k):binary.get(v['status']) for k,v in details.items() if v['required'] or k in legacy}
    return {**result,"technical_review":status,"checks":matches,"check_details":details,"observed":observed,
            "measurement_scope":"Metadados e decodificação local. Sincronia, conteúdo, ação e qualidade artística pedem revisão."}

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
    if cmd=="shot-compare":return compare_handoff(snapshot,spec["handoff"],spec["path"],spec.get("rights_confirmed"))
    if cmd=="shot-link":changes=[link_change(snapshot,spec,spec["from"],spec["to"])]
    if cmd=="shot-repair":
        changes=repair_changes(snapshot,spec)
    if cmd=="shot-import":
        from harness_runtime import import_asset
        from takes import local_media_path
        shot=resolve(ix,spec["shot"])
        require(spec["shot"]["table"]=="Shot List","Import needs a current shot")
        asset=import_asset(local_media_path(spec["path"]),spec.get("kind","FINAL_ASSET"),spec["asset_id"],1,spec["origin"],spec["rights_confirmed"])
        comparison=None
        if "handoff" in spec:
            require(spec["handoff"].get("shot")==spec["shot"],"Handoff belongs to another shot")
            comparison=compare_handoff(snapshot,spec["handoff"],spec["path"],spec["rights_confirmed"])
            require(comparison["media_sha256"]==asset["sha256"],"Imported bytes differ from inspected take")
            failures = [k for k,v in comparison['check_details'].items() if v['required'] and v['status']=='FAIL']
            require(not failures,"Returned take differs from the handoff specification: "+', '.join(failures))
        entry={"table":"Artifact Registry","id":asset["id"],"expected_revision":None,"values":{
            "project_id":shot["project_id"],"episode_id":shot["episode_id"],"is_test":shot["is_test"],"gate_id":"G12","kind":asset["kind"],
            "department":"editing","version":1,"uri":asset["uri"],"sha256":asset["sha256"],"origin":spec["origin"],"rights":spec["rights"],"status":"REVIEW_REQUIRED"}}
        at=stamp()
        draft=prepare(snapshot,{**spec["authorization"],"at":at,"changes":[entry]})
        dest=ref("Artifact Registry",index(draft["candidate"])["Artifact Registry"][asset["id"]])
        provenance={"status":"UNBOUND_LEGACY_IMPORT"}
        if comparison:
            provenance={"status":"DECLARED_RETURN_PACKET", "handoff_sha256":comparison["handoff_sha256"],
                        "media_sha256":asset["sha256"]}
        link=link_change(draft["candidate"],{**spec,"relation":"take"},spec["shot"],dest)
        link["values"]["choice"]=canonical({**json.loads(link["values"]["choice"]),"return_provenance":provenance})
        plan=prepare(snapshot,{**spec["authorization"],"at":at,"changes":[entry,link]})
        return {**plan,"return_provenance":provenance,**({"return_comparison":comparison} if comparison else {})}
    return prepare(snapshot,{**spec["authorization"],"at":stamp(),"changes":changes})

