"""Exercise two episodes locally. All decisions and footage in this rehearsal are test data."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/"scripts"))
from shared_state import prepare,validate,SCHEMA,canonical,index
from episode_workflow import initialize_episode
from series_bible import canon_plan,handoff,check_assumptions
from shot_workflow import dispatch,ref,digest_file
from episode_view import build

def auth(op):
    return {"op_id":"TEST-"+op,"actor":"Ensaio local identificado","authorized":True,"user_message_ref":"SYNTHETIC-DEMO-"+op}
def write(out,name,obj):
    (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def scenario(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    pid="SERIE-AGUA";e1=pid+"-EP1";e2=pid+"-EP2"
    snap={"schema_version":"3.1.0","spreadsheet_id":"LOCAL-DEMO","read_at":now,"tables":{n:[] for n in SCHEMA["tables"]},"scope":{"project_id":pid,"episode_id":e1,"include_test":True}}
    snap=initialize_episode(snap,{"project_id":pid,"project_name":"A última água — ensaio","episode_title":"O cantil","target_seconds":60,"is_test":True,"genre":"guerra"},auth("EP1"))["candidate"]
    items=[("audience_knowledge","AUDIENCE","agua","escassa","O som breve da água denuncia a escassez na chegada."),
           ("character_knowledge","LIA","agua","escassa","Ao servir uma porção na tampa, Lia vê quão pouca água resta."),
           ("character_knowledge","DAVI","chegada","desconhecida","Ele ouve a buzina e não vê quem chega."),
           ("relationship","LIA+DAVI","cuidado","recíproco","Davi aceita beber antes de Lia."),
           ("prop","CANTIL","posse","Lia.direita","Lia troca a mão em quadro depois da entrega."),
           ("location","ESTACAO","porta","W1 oeste","A planta aprovada no ensaio conserva a entrada."),
           ("open_question","ESTACAO","chegada","quem acionou a buzina?","O episódio termina antes da resposta.")]
    beats=["SH01","SH04","SH06","SH05","SH06","SH01","SH06"]
    entries=[{"decision_id":f"D-CANON-{i}","reason":reason,"status":"RECORDED","fact":{"kind":k,"subject":holder,"key":key,"value":val,"beat":beats[i-1],"sequence":int(beats[i-1][2:])*10+i}} for i,(k,holder,key,val,reason) in enumerate(items,1)]
    entries[3]["fact"]["previous_decision_id"]="D-EARLY-CARE"
    entries.insert(0,{"decision_id":"D-EARLY-CARE","status":"RECORDED","reason":"Davi oferece a água. Lia ainda tenta devolver-lhe o cantil.","fact":{"kind":"relationship","subject":"LIA+DAVI","key":"cuidado","value":"oferta unilateral de Davi","beat":"SH03","sequence":30}})
    entries.append({"decision_id":"D-DRAFT","reason":"Hipótese para revisão.","status":"DRAFT","fact":{"kind":"character_knowledge","subject":"DAVI","key":"chegada","value":"uma vizinha","beat":"SH06","sequence":68}})
    snap=canon_plan(snap,{"project_id":pid,"episode_id":e1,"entries":entries,"authorization":auth("CANON")})["candidate"]
    old=snap["tables"]["Episodes"][0].copy()
    snap=initialize_episode(snap,{"project_id":pid,"new_episode":True,"episode_title":"Depois da buzina","target_seconds":60,"include_test":True},auth("EP2"))["candidate"]
    assert snap["tables"]["Episodes"][0]==old
    bible=handoff(snap,pid,e2,before_episode=True);write(out,"handoff-ep2.json",bible)
    checks=check_assumptions(bible,[{"kind":"character_knowledge","subject":"DAVI","key":"chegada","value":"uma vizinha"},{"kind":"character_knowledge","subject":"LIA","key":"chegada","value":"uma vizinha"}])
    assert [r["status"] for r in checks]==["CONFLICT","UNKNOWN"];write(out,"scene-check.json",checks)
    out_ep2=out/"EP2";out_ep2.mkdir(exist_ok=True);build(snap,pid,e2,out_ep2)
    specs=json.loads((Path(__file__).with_name("last-water-shots.json")).read_text(encoding="utf-8"))
    changes=[]
    def add(table,id,values):
        vals={"project_id":pid,"episode_id":e1,"is_test":True,**values}
        changes.append({"table":table,"id":id,"expected_revision":None,"values":vals})
    for s in specs:
        states={"in":{"cantil":s["entry"],"tampa":s["cap_in"]},"out":{"cantil":s["exit"],"tampa":s["cap_out"]}}
        add("Shot List",s["key"],{"gate_id":"G10","version":"1.2-demo","scene_beat":"Estação","order":s["order"],"duration_s":s["duration"],"purpose":s["purpose"],"action":s["action"],"camera_blocking":s["camera"],"sound_edit":s["sound"],"start_end_state":canonical(states),"status":"DRAFT"})
    for s in specs:
        image=f"examples/series-worked/frames/P{s['order']:02d}.png"
        add("Artifact Registry","ART-DEMO-"+s["key"],{"gate_id":"G10","kind":"REFERENCE","department":"composition","version":1,"uri":image,"sha256":digest_file(R/image),"origin":"Cartão esquemático autoral do próprio plano.","rights":"Autoral, autorizado no ensaio","status":"DRAFT"})
    snap=prepare(snap,{**auth("ASSETS"),"at":now,"changes":changes})["candidate"]
    def link(s,op,source,dest,relation,**extra):
        refs=index(s)
        spec={"from":ref(source[0],refs[source[0]][source[1]]),"to":ref(dest[0],refs[dest[0]][dest[1]]),"relation":relation,"decision_id":"LINK-"+op,"reason":"Decisão sintética de encadeamento para o estudo.","authorization":auth(op),**extra}
        return dispatch("shot-link",s,spec,out)["candidate"]
    for s in specs:
        snap=link(snap,s["key"],("Artifact Registry","ART-DEMO-"+s["key"]),("Shot List",s["key"]),"reference",role="image_references")
    snap=link(snap,"HAND",("Shot List","SH05"),("Shot List","SH06"),"uses",field="cantil")
    prompts=[]
    for s in specs:
        pack=dispatch("shot-handoff",snap,{"shot_id":s["key"],"model_id":"seedance_2_5","parameters":{"mode":"omni_reference","resolution":"720p","generate_audio":True}},out)
        write(out,s["key"]+"-manual.json",pack)
        d=pack["delivery"]
        prompts.append({"table":"Prompts","id":"PROMPT-"+s["key"],"expected_revision":None,"values":{"project_id":pid,"episode_id":e1,"is_test":True,"gate_id":"G10","version":"demo-v1","target_table":"Shot List","target_id":s["key"],"model":d["model_id"],"model_checked_at":"2026-11-24","reference_roles":canonical(pack["attachment_order"]),"locked_constraints":d["protected"],"prompt_text":d["prompt"],"native_parameters":canonical(d["native_parameters"]),"status":"DRAFT"}})
    snap=prepare(snap,{**auth("PROMPTS"),"at":now,"changes":prompts})["candidate"]
    source=R/"examples/series-worked/SH06-previs.mp4"
    take=dispatch("shot-import",snap,{"shot":ref("Shot List",index(snap)["Shot List"]["SH06"]),"asset_id":"TAKE-06","path":str(source),"kind":"NARRATIVE_PREVIS","origin":"Animatic esquemático autoral de dez segundos, exclusivo do SH06","rights_confirmed":True,"rights":"Material autoral didático","decision_id":"LINK-RETURN","reason":"Exercitar importação de referência para nova inspeção","authorization":auth("RETURN")},out)
    snap=take["candidate"]
    snap=link(snap,"SELECTED",("Shot List","SH06"),("Artifact Registry","TAKE-06"),"selected_take")
    write(out,"impact-cantil.json",dispatch("shot-impact",snap,{"shot_id":"SH05","field":"cantil"},out));write(out,"storyboard.json",dispatch("storyboard",snap,{"episode_id":e1,"scene_beat":"Estação"},out))
    build(snap,pid,e1,out)
    return snap
if __name__=="__main__":
    directory=Path(sys.argv[1]).resolve()
    if directory.exists() and any(directory.iterdir()):raise SystemExit("Escolha pasta de ensaio vazia.")
    data=scenario(directory);print(json.dumps({"episodes":len(data["tables"]["Episodes"]),"shots":len(data["tables"]["Shot List"]),"output":str(directory),"synthetic":True}))

