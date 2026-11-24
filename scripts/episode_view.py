"""Portable episode guide built from a read copy with decision provenance and shot cards."""
import base64
import mimetypes
from html import escape
from pathlib import Path
from series_bible import handoff
from shot_workflow import card, digest_file, ROOT

LABELS = {"audience_knowledge":"O que o público sabe","character_knowledge":"O que cada personagem sabe",
          "relationship":"Relações","prop":"Objetos","location":"Locações","open_question":"Perguntas em aberto"}
def e(value):
    return escape(str(value),quote=True)

def preview(links,registry):
    for link in links:
        if link["relation"] not in {"reference","storyboard"} or link["stale"]:
            continue
        artifact=registry.get(link["from"]["id"])
        if not artifact or not artifact["rights"].strip():continue
        path=ROOT/Path(artifact["uri"])
        mime=mimetypes.guess_type(path)[0]
        if mime not in {"image/png","image/jpeg","image/webp"} or not path.is_file():continue
        if path.stat().st_size>2_000_000 or digest_file(path)!=artifact["sha256"]:continue
        blob=base64.b64encode(path.read_bytes()).decode("ascii")
        return f'<figure><img src="data:{mime};base64,{blob}" alt="{e(artifact["origin"])}"><figcaption>{e(artifact["origin"])} · versão {e(artifact["version"])}</figcaption></figure>'
    return ""

def build(snapshot,project_id,episode_id,out,include_previous_only=False):
    bible=handoff(snapshot,project_id,episode_id,before_episode=include_previous_only)
    sections=[]
    decisions={f["source"]["id"]:f for f in bible["timeline"]}
    for kind in LABELS:
        items=[]
        for fact in bible["facts"][kind]:
            src=fact["source"]; url=src.get("sheet_url")
            link=f'<p><a href="{e(url)}" target="_blank" rel="noopener">Abrir decisão no Sheets</a></p>' if url else ""
            prev=decisions.get(fact.get("previous_decision_id"))
            before=f'<p>Antes · {e(prev["value"])} ({e(prev["source"]["id"])})</p>' if prev else ""
            subject="Público" if kind=="audience_knowledge" else fact["subject"]
            items.append(f'<li><strong>{e(subject)} · {e(fact["key"])}</strong><br>{e(fact["value"])}{before}<details><summary>Decisão {e(src["id"])} · rev. {e(src["revision"])}</summary><p>{e(src["reason"])}</p><p>EP{e(fact["episode_number"])} · {e(fact["beat"])} · {e(src["message"])}</p>{link}</details></li>')
        sections.append(f'<section><h3>{LABELS[kind]}</h3>'+("<ul>"+"".join(items)+"</ul>" if items else "<p>Ainda sem fato registrado.</p>")+"</section>")
    rows=[r for r in snapshot["tables"]["Shot List"] if r["episode_id"]==episode_id and r["status"]!="ARCHIVED"]
    registry={r["id"]:r for r in snapshot["tables"]["Artifact Registry"]}
    cards=[]
    for row in sorted(rows,key=lambda r:(r["scene_beat"],r["order"],r["id"])):
        c=card(snapshot,row["id"]); states=c["states"]
        def state_text(d):
            return " · ".join(e(k)+" = "+e(v) for k,v in d.items()) if isinstance(d,dict) else e(d)
        state_list="".join(f'<li>{e({"in":"Entrada","out":"Saída"}.get(k,k))} · {state_text(v)}</li>' for k,v in states.items())
        warnings="".join(f'<p>{e(w["status"])} · {e(w["field"])} · {e(w["before"])} → {e(w["after"])}</p>' for w in c["continuity_review"])
        links="".join(f'<li>{e(x["relation"])} · {e(x["from"]["id"])} → {e(x["to"]["id"])} · {"rever versão" if x["stale"] else "versão conferida"}</li>' for x in c["links"])
        t=c["selected_take"];choice=e(t["id"])+" rev. "+str(t["revision"]) if t else "Escolha pendente"
        last=c.get("last_decision"); last_html=f'<p>Última decisão · {e(last["id"])} · {e(last["reason"])}</p>' if last else ""
        cards.append(f'<article><h3>{e(row["id"])} · {e(c["beat"])} · {e(c["duration_s"])} s</h3>{preview(c["links"],registry)}<p><strong>{e(c["intention"])}</strong></p><p>{e(c["action"])}</p><p>Câmera · {e(c["camera"])}<br>Som · {e(c["sound"])}</p><ul>{state_list}</ul>{warnings}<p>Take · {choice}</p>{last_html}<details><summary>Referências e versões</summary><ul>{links}</ul></details></article>')
    proposals="".join(f'<li>{e(p["subject"])} · {e(p["key"])} · {e(p["value"])} ({e(p["source"]["id"])})</li>' for p in bible["proposals"])
    style="""body{color:#eeeae2;background:#182124;font:17px/1.5 system-ui,sans-serif;max-width:980px;margin:auto;padding:clamp(15px,4vw,42px)}h1,h2{color:#f5d599}h2{margin-top:36px}h3{margin:.4em 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:16px}section,article{border-top:1px solid #627476;padding:14px 0}article{display:flow-root}a,summary{color:#b1dce9}li{padding:3px}small,figcaption{color:#c3ccca}figure{max-width:400px;margin:0 0 10px 18px;float:right}img{width:100%;height:auto}figcaption{font-size:.8em}@media(max-width:680px){figure{float:none;margin:0}}"""
    doc=f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bíblia e planos do episódio</title><style>{style}</style><main><h1>Bíblia do episódio {bible["episode_number"]}</h1><small>{e(project_id)} / {e(episode_id)} · leitura {e(snapshot["read_at"])}</small>'
    if any(r["id"]==episode_id and r["is_test"] for r in snapshot["tables"]["Episodes"]): doc+='<p>Ensaio didático com decisões simuladas.</p>'
    doc+='<div class="grid">'+"".join(sections)+'</div><h2>Propostas em revisão</h2>'+("<ul>"+proposals+"</ul>" if proposals else "<p>Nenhuma proposta pendente.</p>")+"<h2>Planos</h2>"+("".join(cards) or "<p>Decupagem pendente.</p>")+"</main></html>"
    path=Path(out)/"episode-guide.html"; path.write_text(doc,encoding="utf-8")
    return {"guide":str(path),"episode_id":episode_id,"facts":sum(map(len,bible["facts"].values())),"shot_count":len(cards),"source_read_at":snapshot["read_at"]}

