'use strict';
const cfg=window.CPE_CONFIG, $=id=>document.getElementById(id);
let snapshot=null, selected='G0', drafts={}, board='phase';
let restoredNeedsFresh=false;
let pendingReconcile=null;
let draftEpoch=0;
let advancedEdited=false;
function invalidatePrepared(clearAuthorization=false){
 draftEpoch++;
 $('outgoing').value='';$('outgoing').hidden=true;$('copy').disabled=true;
 if($('decisionSummary')){$('decisionSummary').hidden=true;$('decisionSummary').textContent='';}
 if(clearAuthorization)$('authorize').checked=false;
}
function previewDecision(title,target,revision,choice,reason){
 const area=$('decisionSummary');if(!area)return;
 const episode=snapshot?.tables.Episodes.find(e=>e.id===snapshot.scope.episode_id);
 const context=episode?.title||window.CPE_DESK_DATA?.episode?.title||'Novo projeto';
 area.textContent=[context,title,target,revision?'Revisão '+revision:'',choice,reason].filter(Boolean).join(' · ');
 area.hidden=false;
}
function registerEdit(){advancedEdited=true;invalidatePrepared(true);saveWorkshop();}
function workshopKey(s){
 return s?'cpe-workshop/1.3/'+JSON.stringify([s.spreadsheet_id,s.scope?.project_id || s.series?.id,s.scope?.episode_id || s.episode?.id]):'';
}
function saveWorkshop(){
 const base=snapshot || window.CPE_DESK_DATA;
 if(!base||!advancedEdited)return;
 try{localStorage.setItem(workshopKey(base),JSON.stringify({selected,board,drafts,support_drafts:supportDrafts,base_read_at:base.read_at}));}
 catch{say('O navegador não conseguiu guardar o rascunho. Faça uma cópia antes de sair.',true);}
}
const DONE=new Set(['APPROVED','LOCKED','SKIPPED']);
const node=(parent,tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;parent.append(n);return n};
function say(text,error=false){$('message').textContent=text;$('message').className=error?'warn':'muted';}
function current(){return snapshot?snapshot.tables.Workflow.find(w=>w.episode_id===snapshot.scope.episode_id&&w.gate_id===selected):window.CPE_DESK_DATA?.workflow?.find(w=>w.gate_id===selected);}
function getDraft(){if(!drafts[selected])drafts[selected]={values:{},checks:{},reason:'',reference:''};return drafts[selected];}
function validateSnapshot(x){
 if(x.schema_version!=='3.1.0'||!x.spreadsheet_id||!x.read_at||!x.scope?.episode_id||!x.tables)throw Error('Cópia incompatível. Peça ao agente um snapshot V3.1.');
 if(JSON.stringify(Object.keys(x.tables).sort())!==JSON.stringify(cfg.tables.slice().sort()))throw Error('Cópia incompleta: faltam abas de estado.');
 const ids=new Set();for(const [name,rows] of Object.entries(x.tables)){if(!Array.isArray(rows))throw Error('Tabela inválida: '+name);for(const r of rows){if(!r.id||ids.has(r.id)||!Number.isInteger(r.revision)||r.revision<1||typeof r.is_test!=='boolean')throw Error('ID/revisão inválido');ids.add(r.id);}}
 const wf=x.tables.Workflow.filter(w=>w.episode_id===x.scope.episode_id);if(wf.length!==16||new Set(wf.map(w=>w.gate_id)).size!==16)throw Error('São necessários os 16 gates do episódio.');
 for(const g of cfg.gates){const w=wf.find(w=>w.gate_id===g.id);if(!w||!cfg.statuses.includes(w.status))throw Error('Gate inválido');const checks=x.tables.Checklists.filter(c=>c.workflow_id===w.id);if(checks.length!==g.checks.length)throw Error('Checklist incompleto');}
 return x;
}
function input(parent,label,key,value,options,disabled=false){const wrap=node(parent,'label',undefined,'field');node(wrap,'span',label);const n=node(wrap,options?'select':'input');n.dataset.key=key;if(options)for(const opt of options){const o=node(n,'option',opt);o.value=opt;}n.value=value??'';n.disabled=disabled;n.oninput=()=>getDraft().values[key]=n.value;return n;}
function render(){
 if($('boardPanel')){$('boardPanel').hidden=true;$('panel').hidden=false;$('boardSelect').value='';}
 const w=current(),g=cfg.gates.find(x=>x.id===selected),d=getDraft(),locked=w&&DONE.has(w.status);
 const projected=!snapshot && window.CPE_DESK_DATA;
 $('scope').textContent=snapshot?`${snapshot.scope.project_id} / ${snapshot.scope.episode_id}${snapshot.scope.include_test?' · TESTE':''}`:projected?projected.series.name+' / '+projected.episode.title:'Nenhum estado importado';
 $('freshness').textContent=restoredNeedsFresh?'Rascunho recuperado. Importe uma cópia atual do agente para conferir a base antes de preparar a mensagem.':snapshot?`Cópia consultada em ${snapshot.read_at}. Pode ter mudado; o agente relerá a planilha.`:'O agente consulta a planilha na conversa. A importação de cópia aqui é opcional.';
 const wf=snapshot?.tables.Workflow.filter(x=>x.episode_id===snapshot.scope.episode_id)??projected?.workflow??[];
 const completed=wf.filter(x=>DONE.has(x.status)).length;$('progressText').textContent=wf.length?`${completed}/16 etapas concluídas na leitura`:'Progresso depende de leitura do agente';$('progress').value=completed;
 $('nav').replaceChildren();for(const gate of cfg.gates){const b=node($('nav'),'button',`${gate.id} · ${gate.name}`);b.className=gate.id===selected?'active':'';b.onclick=()=>{invalidatePrepared(true);selected=gate.id;board='phase';render();saveWorkshop();};}
 const p=$('panel');p.replaceChildren();node(p,'h2',g.id+' · '+g.name);node(p,'p',w?`Estado na cópia: ${w.status} · revisão ${w.revision}`:'Rascunho sem estado de produção','muted');
 const unmet=g.depends.filter(id=>!DONE.has(wf.find(x=>x.gate_id===id)?.status));node(p,'p',g.depends.length?(unmet.length?'Dependências pendentes: '+unmet.join(', '):'Dependências satisfeitas na cópia'):'Marco inicial',unmet.length?'warn':'muted');
 node(p,'p',cfg.guidance[selected]);
 const fields=node(p,'div',undefined,'fields');for(const f of cfg.fields[selected])input(fields,f.label,f.key,d.values[f.key]??f.value??'',f.options,!!locked);
 const a=node(p,'article');node(a,'h3','Revisão e evidências');node(a,'p','Entrega esperada: '+g.deliverable);
 const rows=snapshot?.tables.Checklists.filter(c=>c.workflow_id===w?.id).sort((a,b)=>a.item_index-b.item_index)??g.checks.map((criterion,i)=>({id:'UNBOUND-'+i,criterion,checked:false,evidence:''}));
 for(const r of rows){const draft=d.checks[r.id]??{checked:r.checked,evidence:r.evidence};d.checks[r.id]=draft;const box=node(a,'div',undefined,'check');const label=node(box,'label');const check=node(label,'input');check.type='checkbox';check.checked=draft.checked;check.disabled=!!locked;label.append(document.createTextNode(r.criterion));const evidence=node(box,'input');evidence.placeholder='Origem, versão e observação deste critério';evidence.value=draft.evidence;evidence.disabled=!!locked;check.onchange=()=>{draft.checked=check.checked;};evidence.oninput=()=>draft.evidence=evidence.value;}
 const reason=input(p,'Motivo da revisão/dispensa ou observação','reason',d.reason);reason.oninput=()=>d.reason=reason.value;
 const reference=input(p,'Referência manual ou ID/versão a reutilizar','reference',d.reference);reference.oninput=()=>d.reference=reference.value;
 const actions=node(p,'div',undefined,'row');const list=[['SAVE_CHOICES','Preparar escolhas'],['REVIEW','Preparar revisão'],['APPROVE','Preparar aprovação'],['LOCK','Preparar bloqueio'],['REVISE','Pedir correção'],['SKIP','Pedir dispensa/reuso'],['IMPORT_REFERENCE','Referenciar material'],['REUSE','Reutilizar versão']];
 for(const [action,label] of list){const b=node(actions,'button',label);b.onclick=()=>prepare(action);b.disabled=!snapshot||action==='APPROVE'&&(w?.status!=='REVIEW_REQUIRED'||unmet.length>0)||action==='LOCK'&&w?.status!=='APPROVED'||action==='SKIP'&&(!g.skippable||!!locked||unmet.length>0)||['SAVE_CHOICES','REVIEW','IMPORT_REFERENCE'].includes(action)&&!!locked;}
 if(!snapshot && !projected){const b=node(actions,'button','Preparar início do projeto');b.onclick=()=>prepare('INIT');}
 if(projected){
  const a=node(actions,'a','Abrir material da etapa');a.href=['G3','G4'].includes(selected)?'#roteiro':selected==='G13'?'#takes':'#planos';
  node(p,'p','Para registrar sua escolha, diga o material e a mudança na conversa.','muted');
 }
}
function stable(x){if(Array.isArray(x))return x.map(stable);if(x&&typeof x==='object')return Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])]));return x;}
async function sha(x){const bytes=new TextEncoder().encode(JSON.stringify(stable(x)));const hash=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(hash)].map(b=>b.toString(16).padStart(2,'0')).join('');}
async function guards(x){const out={};for(const [name,rows] of Object.entries(x.tables)){if(name==='Revision History')continue;out[name]={};for(const r of rows)out[name][r.id]=await sha(r);}return out;}
async function prepare(action){
 invalidatePrepared();const preparation=draftEpoch;
 try{
  if(!$('authorize').checked)throw Error('Marque a autorização antes de preparar a mensagem. Nada foi enviado ou salvo.');
  if(restoredNeedsFresh)throw Error('Confira o rascunho com uma leitura atual antes de enviar.');
  const d=getDraft(),w=current(),g=cfg.gates.find(x=>x.id===selected);
  if(['REVISE','SKIP'].includes(action)&&!d.reason.trim())throw Error('Informe o motivo.');
  if(['IMPORT_REFERENCE','REUSE'].includes(action)&&!d.reference.trim())throw Error('Informe uma referência ou ID/versão.');
  if(action==='APPROVE'&&Object.values(d.checks).some(c=>!c.checked||!c.evidence.trim()))throw Error('Cada critério precisa de marcação e evidência.');
  if(action==='INIT'&&!d.values.project_name?.trim())throw Error('Informe o nome do projeto no painel inicial.');
  const payload={contract:'cpe-intent-3.1',intent_id:crypto.randomUUID(),action,spreadsheet_id:snapshot?.spreadsheet_id??cfg.spreadsheet_id,scope:snapshot?.scope??null,gate_id:selected,base_read_at:snapshot?.read_at??null,expected_revision:w?.revision??null,base_scope_sha256:snapshot?(snapshot.scope_guards_sha256??await sha(await guards(snapshot))):null,choices:d.values,checklist:d.checks,reason:d.reason,reference:d.reference,authorized:true,credits_allowed:0};
  if(preparation!==draftEpoch||!$('authorize').checked)return;
  const titles={SAVE_CHOICES:'Registrar escolhas',REVIEW:'Solicitar revisão',APPROVE:'Aprovar etapa',LOCK:'Bloquear versão',REVISE:'Solicitar correção',SKIP:'Solicitar dispensa',IMPORT_REFERENCE:'Incluir referência',REUSE:'Reutilizar material',INIT:'Iniciar projeto'};
  previewDecision(titles[action]||action,g.name,w?.revision,Object.values(d.values).filter(v=>typeof v==='string'&&v.trim()).join(' · '),d.reason||d.reference);
  $('outgoing').value='Autorizo a alteração abaixo após validar e reler o estado atual. Se houver conflito, apresente-o sem gravar.\nCPE_INTENT\n'+JSON.stringify(payload,null,2);
  $('outgoing').hidden=false;$('copy').disabled=false;say('Mensagem preparada. Copie e envie como nova mensagem ao agente. Nada foi enviado ou gravado neste painel.');
 }catch(e){say(e.message,true);}
}
$('import').onclick=()=>$('file').click();
function cleanDraftMap(input,allowedIds){
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Rascunhos inválidos.');
 const mapped={};
 for(const [key,draft] of Object.entries(input)){
  if(!allowedIds.includes(key)||!draft||typeof draft!=='object'||Array.isArray(draft))throw Error('Painel de rascunho desconhecido.');
  if(!draft.values||typeof draft.values!=='object'||!draft.checks||typeof draft.checks!=='object')throw Error('Campos do rascunho incompletos.');
  mapped[key]=draft;
 }
 return mapped;
}
function resetSupports(saved={}){
 for(const key of Object.keys(supportDrafts))delete supportDrafts[key];
 Object.assign(supportDrafts,saved);
}
function showCurrent(){
 if(board==='phase')render();else showBoard(board);
}
function draftFile(){
 return {kind:'LOCAL_DRAFT_NOT_SAVED',format_version:2,snapshot,drafts,support_drafts:supportDrafts,selected,board};
}
function restoreDraft(data){
 const phases=cfg.gates.map(g=>g.id);
 const boards=window.CPE_BOARDS.map(b=>b.id);
 const base=data.snapshot===null?null:validateSnapshot(data.snapshot);
 const phaseDrafts=cleanDraftMap(data.drafts,phases);
 const boardDrafts=cleanDraftMap(data.support_drafts??{},boards);
 if(!phases.includes(data.selected)||!['phase',...boards].includes(data.board??'phase'))throw Error('Seleção de painel inválida.');
 snapshot=base;drafts=phaseDrafts;resetSupports(boardDrafts);selected=data.selected;board=data.board??'phase';
 pendingReconcile=null;drawReconciliation();restoredNeedsFresh=Boolean(base);advancedEdited=true;invalidatePrepared(true);showCurrent();
 say(base?'Rascunho recuperado. Importe agora a cópia atual do episódio para conferir as versões.':'Rascunho inicial recuperado.');
}
function changedRecords(oldState,fresh){
 const changes=[];
 for(const [table,rows] of Object.entries(oldState.tables)){
  if(table==='Revision History')continue;
  const old=new Map(rows.map(r=>[r.id,r])),now=new Map(fresh.tables[table].map(r=>[r.id,r]));
  for(const id of new Set([...old.keys(),...now.keys()])){
   const before=old.get(id),after=now.get(id);
   if(JSON.stringify(stable(before))===JSON.stringify(stable(after)))continue;
   const row=after??before;
   const sameProject=row.project_id===fresh.scope.project_id;
   if(!sameProject&&row.project_id!=='LIB-CPE31')continue;
   if(sameProject&&row.episode_id&&row.episode_id!==fresh.scope.episode_id)continue;
   const fields=Object.keys(row).filter(k=>!['updated_by','updated_at','last_op_id','revision'].includes(k)&&before?.[k]!==after?.[k]);
   changes.push({table,id,before:before?.revision??null,after:after?.revision??null,fields});
  }
 }
 return changes;
}
function drawReconciliation(){
 const panel=$('reconcile');if(!panel)return;panel.replaceChildren();panel.hidden=!pendingReconcile;
 if(!pendingReconcile)return;
 node(panel,'h3','Conferir mudanças antes de recuperar');
 for(const change of pendingReconcile.changes){
  node(panel,'p',change.table+' / '+change.id+' · revisão '+(change.before??'ausente')+' → '+(change.after??'ausente')+' · '+(change.fields.join(', ')||'metadados'));
 }
 for(const [mode,title] of [['notes','Conservar anotações, reconferir marcações e alvos'],['discard','Usar a leitura atual e descartar o rascunho']]){
  const b=node(panel,'button',title);b.onclick=()=>resolveDraftConflict(mode);
 }
}
function resolveDraftConflict(mode){
 if(!pendingReconcile||!['notes','discard'].includes(mode))return;
 snapshot=pendingReconcile.fresh;pendingReconcile=null;restoredNeedsFresh=false;$('authorize').checked=false;
 if(mode==='notes'){
  for(const d of Object.values(drafts)){d.checks={};d.reference='';}
  for(const d of Object.values(supportDrafts)){d.checks={};d.target='';delete d.values.packet;delete d.values.choice;}
 }else{drafts={};resetSupports();selected='G0';board='phase';}
 $('outgoing').value='';$('outgoing').hidden=true;$('copy').disabled=true;drawReconciliation();showCurrent();
 say('Cópia atualizada. Confira os materiais e expresse uma nova decisão.');
}
async function importState(data){
 const fresh=validateSnapshot(data);
 const matchesScope=!!snapshot && workshopKey(fresh)===workshopKey(snapshot);
 invalidatePrepared(true);
 if(restoredNeedsFresh || (advancedEdited && matchesScope)){
  if(!matchesScope)throw Error('Projeto, episódio ou planilha diferente. Seu rascunho permanece aberto. Use a cópia do episódio original.');
  const changes=changedRecords(snapshot,fresh);
  if(changes.length){pendingReconcile={fresh,changes};restoredNeedsFresh=true;drawReconciliation();throw Error('Conflito de versões. Seu rascunho foi preservado. Confira os registros alterados antes de escolher como recuperar.');}
  snapshot=fresh;pendingReconcile=null;drawReconciliation();restoredNeedsFresh=false;showCurrent();say('Versões conferidas. Revise suas escolhas e autorize uma nova mensagem.');return;
 }
 saveWorkshop();
 snapshot=fresh;pendingReconcile=null;drawReconciliation();drafts={};resetSupports();selected='G0';board='phase';advancedEdited=false;
 const recovered=restoreWorkshop(fresh);
 showCurrent();say(recovered?'Anotações recuperadas para este episódio. Confira a versão antes de uma nova decisão.':'Cópia carregada. O agente validará a escolha no Sheets.');
}
function restoreWorkshop(base){
 try{
  const local=JSON.parse(localStorage.getItem(workshopKey(base))||'null');
  if(local && cfg.gates.some(g=>g.id===local.selected)){
   drafts=cleanDraftMap(local.drafts,cfg.gates.map(g=>g.id));
   const supports=cleanDraftMap(local.support_drafts||{},window.CPE_BOARDS.map(b=>b.id));
   if(local.base_read_at!==base.read_at){
    for(const d of Object.values(drafts)){d.checks={};d.reference='';}
    for(const d of Object.values(supports)){d.checks={};d.target='';delete d.values.packet;delete d.values.choice;}
   }
   resetSupports(supports);selected=local.selected;board=window.CPE_BOARDS.some(b=>b.id===local.board)?local.board:'phase';advancedEdited=true;return true;
  }
 }catch{/* File mode can deny local storage. The manual draft import remains available. */}
 return false;
}
$('file').onchange=async e=>{
 $('outgoing').value='';$('outgoing').hidden=true;$('copy').disabled=true;$('authorize').checked=false;
 try{
  const f=e.target.files[0];if(!f)return;
  if(f.size>10000000)throw Error('Arquivo muito grande. Peça uma cópia limitada ao projeto.');
  const data=JSON.parse(await f.text());
  if(data.kind==='LOCAL_DRAFT_NOT_SAVED')restoreDraft(data);else await importState(data);
 }catch(err){say(err.message,true);}finally{e.target.value='';}
};
$('copy').onclick=async()=>{if(!$('authorize').checked||$('copy').disabled||!$('outgoing').value){invalidatePrepared();return;}try{await navigator.clipboard.writeText($('outgoing').value);say('Copiado. Envie ao agente em nova mensagem.');}catch{ $('outgoing').focus();$('outgoing').select();say('Selecione e copie o texto. O navegador não permitiu cópia automática.');}};
$('export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(draftFile(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='cpe-local-draft-not-saved.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);say('Rascunho exportado com a fase e os painéis de apoio.');};
$('authorize').onchange=()=>invalidatePrepared();
for(const id of ['panel','boardPanel']){
 $(id)?.addEventListener?.('input',registerEdit);
 $(id)?.addEventListener?.('change',registerEdit);
}
render();
