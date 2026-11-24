"""Select references by episode, technique, genre and concrete directorial intention."""
import json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GATE_DEPTS={"G1":{"research","design"},"G2":{"narrative","story"},"G3":{"narrative","emotion"},"G4":{"narrative","screenplay","dialogue"},"G5":{"optics","light","composition","direction"},"G7":{"casting","performance","design"},"G8":{"design","geometry","locations","composition"},"G9":{"design","props"},"G10":{"optics","direction","composition","continuity"},"G13":{"sound","editing"},"G14":{"continuity","editing","sound"}}
def words(text):
    text=unicodedata.normalize("NFKD",str(text).lower())
    return set(re.findall("[a-z0-9]+","".join(c for c in text if not unicodedata.combining(c))))-{"de","a","as","os","o","em","do","da","um","para","com","the","e"}
def matching_genre_cases(genre):
    cases=json.loads((ROOT/"knowledge/genre-cases.json").read_text(encoding="utf-8"))
    terms=words(genre)
    return [case for case in cases if any(words(alias)<=terms for alias in [case["genre"],*case["aliases"]])]

def genre_case(genre):
    return next(iter(matching_genre_cases(genre)),None)

def select(snapshot,project,episode,gate,facets,model,intention,*,confirmed_messages=()):
    project_id,episode_id=project["id"],episode["id"]
    depts=set(facets)|GATE_DEPTS.get(gate,set())
    keywords=words(intention)
    genres=words(episode["genre"])
    techniques={t["id"]:t for t in snapshot["tables"]["Techniques"]}
    results,explanations={},{}
    for table in ("Techniques","Examples","Reference Library","Creative Preferences","Production Lessons","Model Compatibility","Human Feedback","Failure Diagnostics","Evaluation Results"):
        ranked=[]
        for row in snapshot["tables"][table]:
            if table=="Human Feedback" and (row["target_table"]=="Pairwise Comparisons" or row["is_test"]
                    or row["status"] not in {"APPROVED","LOCKED"} or row["user_message_ref"] not in confirmed_messages):continue
            if table=="Examples" and row["kind"]=="TAKE_COMPARISON":continue
            local=row["project_id"]==project_id and row["episode_id"] in ("",episode_id)
            shared=row["project_id"]=="LIB-CPE31" and table in {"Techniques","Examples","Reference Library","Production Lessons","Model Compatibility","Creative Preferences"}
            if not (local or shared) or row["status"] in {"ARCHIVED","REJECTED"}:continue
            if shared and table=="Creative Preferences" and row.get("category")!="USER_CONSTRAINT":continue
            if table=="Model Compatibility" and model and row.get("model_id")!=model:continue
            technique=techniques.get(row.get("technique_id"),{})
            dep=row.get("department",technique.get("department",""))
            descriptor=" ".join(str(row.get(k,"")) for k in ("title","name","context","expected","when_to_use","observation","scope"))
            matches=keywords&words(descriptor+" "+technique.get("when_to_use",""))
            reasons=[]
            if matches:reasons.append("intenção: "+", ".join(sorted(matches)))
            if dep in depts:reasons.append("departamento: "+dep)
            genre_match=genres&words(descriptor)
            if genre_match:reasons.append("gênero: "+", ".join(sorted(genre_match)))
            if local:reasons.append("contexto do projeto")
            if model and row.get("model_id")==model:reasons.append("modelo escolhido")
            constraint=(table=="Creative Preferences" and row.get("category")=="USER_CONSTRAINT"
                        and row["status"] in {"APPROVED","LOCKED"})
            if constraint:reasons.append("restrição explícita")
            if not reasons and dep!="integrated":continue
            score=50*constraint+12*bool(matches)+min(len(matches),8)+8*(dep in depts)+6*bool(genre_match)+4*local+2*(row["status"] in {"APPROVED","LOCKED"})
            ranked.append((-score,row["id"],row,reasons or ["exemplo integrado"]))
        ranked.sort(key=lambda item:(item[0],item[1]))
        chosen=ranked if table=="Creative Preferences" else ranked[:8]
        results[table]=[x[2] for x in chosen]
        explanations[table]=[{"id":x[1],"why":x[3],"apply":x[2].get("context") or x[2].get("procedure") or x[2].get("expected") or ""} for x in chosen]
    return results,explanations
