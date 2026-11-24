'use strict';
const supportDrafts={};
const registerTypes=new Set(['environment','media-inspector','execution-evidence','quality-benchmark','recovery','failure','causal-diagnosis']);
const experimentTypes=new Set(['visual-lab','experiment','optical-lab','blender-previs','prompt-lab','composition-analyzer']);
const comparisonTypes=new Set(['cast-compare','location-compare','props-compare','revision-comparison']);
function boardActions(id){
 if(id==='blind-comparison')return [['COMPARE','Registrar voto sobre o par']];
 if(comparisonTypes.has(id))return [['SELECT','Registrar escolha'],['REQUEST_REVISION','Pedir outra opção']];
 if(experimentTypes.has(id))return [['CONFIGURE','Propor experimento'],['REUSE','Reutilizar versão']];
 if(registerTypes.has(id))return [['SELECT','Registrar observação'],['REQUEST_REVISION','Pedir revisão']];
 if(id==='reference-approval'||id==='judgment')return [['APPROVE','Aprovar material'],['REJECT','Solicitar outra proposta']];
 if(id==='production-export'||id==='asset-import')return [['SELECT','Selecionar versão'],['REQUEST_REVISION','Solicitar ajuste']];
 return [['SELECT','Registrar escolha'],['REUSE','Reutilizar versão'],['REQUEST_REVISION','Pedir ajuste']];
}
function findBoardMaterials(b){
 if(snapshot){
  const scope=snapshot.scope;
  return (snapshot.tables[b.table]||[]).filter(r=>r.project_id===scope.project_id&&(!r.episode_id||r.episode_id===scope.episode_id) || r.project_id==='LIB-CPE31');
 }
 return window.CPE_DESK_DATA?.materials?.[b.table]||[];
}
function materialName(r){return r.label||r.title||r.name||r.character_name||r.asset_name||r.topic||r.scene_beat||r.id;}
const taskCriteria={
 'cast-compare':['A escuta e a reação de cada intérprete foram revistas no mesmo trecho','O gesto escolhido atende ao objetivo da cena','A decisão inclui o take e a versão'],
 'location-compare':['O eixo e os acessos são legíveis','A posição da luz permite montar os planos previstos','O lugar escolhido e sua versão foram identificados'],
 'props-compare':['O objeto pode ser reconhecido no enquadramento','Posse, mão e estado foram conferidos na passagem entre planos','A referência usada tem versão e origem'],
 'reference-approval':['A origem e os direitos foram identificados','A referência serve à intenção declarada','A versão apresentada é a que será aprovada'],
 'blind-comparison':['O par e as duas versões foram identificados','A marca decisiva foi revista em A e B','O motivo e o alcance da preferência foram indicados'],
 'media-inspector':['O arquivo e o intervalo examinado foram identificados','As faixas disponíveis foram analisadas','A evidência indica o instante e os limites do teste'],
 'blender-previs':['Câmera e posição correspondem à cena','A trajetória prevista cabe no cenário','O arquivo salvo pôde ser reaberto'],
 'production-export':['O modelo e os campos de entrada foram conferidos','As referências aparecem na ordem e versão corretas','A execução manual e os critérios de retorno estão claros'],
 'asset-import':['Origem e direitos do arquivo estão identificados','A versão do plano de origem está correta','A nova mídia seguirá para avaliação'],
 'correction-control':['O campo a corrigir está identificado','As versões dependentes foram conferidas','O material preservado continua acessível']
};
function criteria(b){
 if(taskCriteria[b.id])return taskCriteria[b.id];
 if(experimentTypes.has(b.id))return ['A hipótese foi formulada para este plano','As versões permitem isolar a mudança examinada','O resultado e os limites da observação estão registrados'];
 if(registerTypes.has(b.id))return ['A observação identifica material e versão','O fato observado tem evidência localizável','A limitação da verificação foi registrada'];
 return b.checklist;
}
function showBoard(id){
 const b=window.CPE_BOARDS.find(x=>x.id===id);if(!b){board='phase';render();return;}
 invalidatePrepared(true);
 selected=b.gate;board=id;render();$('boardSelect').value=id;$('panel').hidden=true;
 const p=$('boardPanel');p.hidden=false;p.replaceChildren();
 const d=supportDrafts[id]??={values:{},checks:{},observation:'',target:''};
 node(p,'h2',b.title);
 const materials=findBoardMaterials(b);
 const wrapper=node(p,'label',undefined,'field');node(wrapper,'span','Consultar material');
 const chooser=node(wrapper,'select');const first=node(chooser,'option','Escolher por nome…');first.value='';
 for(const r of materials){const opt=node(chooser,'option',materialName(r)+' · rev. '+r.revision);opt.value=r.id;}
 const context=node(p,'div');
 function describe(r){
  context.replaceChildren();
  if(!r)return;
  node(context,'h3',materialName(r));
  for(const [key,title] of [['status','Situação'],['version','Versão'],['description','Descrição'],['excerpt','Trecho'],['summary','Resumo'],['evidence','Evidência'],['origin','Origem'],['purpose','Intenção'],['action','Ação'],['observation','Observação']]){
   if(typeof r[key]==='string'&&r[key].trim())node(context,'p',title+' · '+r[key]);
  }
 }
 const previous=materials.find(r=>d.target===r.id+' rev'+r.revision);
 if(previous){chooser.value=previous.id;describe(previous);}
 if(!materials.length)node(context,'p','Ainda sem material desta categoria na leitura.','muted');
 const fields=node(p,'div',undefined,'fields');
 for(const f of b.fields){const wrap=node(fields,'label',undefined,'field');node(wrap,'span',f.label);const el=node(wrap,f.options?'select':'input');if(f.options){const empty=node(el,'option','Escolha…');empty.value='';for(const value of f.options){const o=node(el,'option',value);o.value=value;}}el.value=d.values[f.key]??'';el.dataset.key=f.key;el.oninput=()=>d.values[f.key]=el.value;}
 if(id==='blind-comparison'){const link=node(p,'a','Comparar takes com imagem, som e marca de tempo');link.href='takes.html';}
 const target=input(p,'Material e revisão selecionados','target',d.target,null,Boolean(materials.length));target.oninput=()=>d.target=target.value;
 chooser.onchange=()=>{
  const r=materials.find(x=>x.id===chooser.value);describe(r);d.target=r?r.id+' rev'+r.revision:'';target.value=d.target;
  d.values={};
  for(const el of fields.querySelectorAll?.('[data-key]')||[]){
   const raw=r?.[el.dataset.key];el.value=typeof raw==='string'||typeof raw==='number'?String(raw):'';
   if(el.value)d.values[el.dataset.key]=el.value;
  }
  d.checks={};for(const i of p.querySelectorAll?.('input[type=checkbox]')||[])i.checked=false;registerEdit();
 };
 const observation=input(p,'Motivo, evidência e pendências','observation',d.observation);observation.oninput=()=>d.observation=observation.value;
 const detail=node(p,'details');node(detail,'summary','Conferir antes de aprovar');
 for(const [i,text] of criteria(b).entries()){const label=node(detail,'label',undefined,'check');const el=node(label,'input');el.type='checkbox';el.checked=!!d.checks[i];el.onchange=()=>d.checks[i]=el.checked;label.append(document.createTextNode(text));}
 const actions=node(p,'div',undefined,'row');
 for(const [action,title] of boardActions(id)){const btn=node(actions,'button',title);btn.disabled=!snapshot;btn.onclick=()=>prepareBoard(id,action);}
 if(!snapshot)node(p,'p','Consulte os materiais aqui. Para registrar, diga na conversa qual versão escolheu e o motivo.','muted');
 saveWorkshop();
}
async function prepareBoard(id,action){
 invalidatePrepared();const preparation=draftEpoch;
 try{
  if(!$('authorize').checked)throw Error('Marque a autorização para preparar a mensagem.');
  if(!snapshot)throw Error('Consulte o estado com o agente primeiro.');
  if(restoredNeedsFresh)throw Error('Confira o rascunho com uma leitura atual antes de enviar.');
  const b=window.CPE_BOARDS.find(x=>x.id===id),d=supportDrafts[id];
  if(!b||!['SELECT','COMPARE','CONFIGURE','APPROVE','REJECT','REQUEST_REVISION','REUSE'].includes(action))throw Error('Ação inválida.');
  if(!d.observation.trim())throw Error('Informe motivo e evidência.');
  if(id==='blind-comparison'&&(!d.values.packet?.trim()||!['A','B','TIE','BOTH_FAIL'].includes(d.values.choice)))throw Error('Identifique o par e escolha explicitamente A, B, empate ou reprovar ambos.');
  if(['APPROVE','REJECT','REQUEST_REVISION','REUSE'].includes(action)&&!d.target.trim())throw Error('Informe ID e revisão do material.');
  if(action==='APPROVE'&&criteria(b).some((_,i)=>!d.checks[i]))throw Error('Confira todos os critérios antes de propor aprovação.');
  const payload={contract:'cpe-intent-3.1',intent_id:crypto.randomUUID(),action:'BOARD_'+action,board_id:id,target_table:b.table,target_ref:d.target,gate_id:b.gate,spreadsheet_id:snapshot.spreadsheet_id,scope:snapshot.scope,base_read_at:snapshot.read_at,base_scope_sha256:snapshot.scope_guards_sha256??await sha(await guards(snapshot)),choices:d.values,observation:d.observation,checklist:d.checks,authorized:true,credits_allowed:0};
  if(preparation!==draftEpoch||!$('authorize').checked)return;
  const target=findBoardMaterials(b).find(r=>d.target===r.id+' rev'+r.revision);
  const title=boardActions(id).find(row=>row[0]===action)?.[1] || b.title;
  previewDecision(title,target?materialName(target):d.target||b.title,target?.revision,d.values.choice||'',d.observation);
  $('outgoing').value='Autorizo esta decisão no escopo indicado após leitura atual, validação e conferência de conflitos.\nCPE_INTENT\n'+JSON.stringify(payload,null,2);$('outgoing').hidden=false;$('copy').disabled=false;say('Mensagem preparada. Envie ao agente em nova mensagem.');
 }catch(e){say(e.message,true);}
}
for(const b of window.CPE_BOARDS){const opt=node($('boardSelect'),'option',b.title);opt.value=b.id;}
$('boardSelect').onchange=()=>showBoard($('boardSelect').value);
if(window.CPE_DESK_DATA?.version===1){
 const active=window.CPE_DESK_DATA.workflow?.find(w=>w.status==='IN_PROGRESS');
 if(active && cfg.gates.some(g=>g.id===active.gate_id))selected=active.gate_id;
 restoreWorkshop(window.CPE_DESK_DATA);
 showCurrent();
}
