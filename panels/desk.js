/* Episode view. Projected by the agent; all browser edits are private local drafts. */
'use strict';
(() => {
  const host = document.getElementById('desk');
  if (!host) return;
  const view = window.CPE_DESK_DATA;
  const ready = view?.version === 1 && view.series?.id && view.episode?.id;
  if(ready && /^https:\/\/docs\.google\.com\/spreadsheets\/d\/[\w-]+\/edit(?:[?#][^\s]*)?$/.test(view.dashboard_url||'')){
    const sheet=document.getElementById('sheetLink');if(sheet)sheet.href=view.dashboard_url;
  }
  const shots = ready ? [...(view.shots || [])] : [];
  const selectedShot = id => shots.find(s => s.id === id);
  function shotName(shot){
    const short=String(shot.id).match(/(?:^|[-_/])(SH\d+[A-Z]?)$/i)?.[1].toUpperCase();
    const label=String(shot.label || '').trim();
    if(!label || label===shot.id)return short || shot.id;
    if(short && !label.toUpperCase().startsWith(short))return short+' · '+label;
    return label;
  }
  const storageKey = ready ? 'cpe-studio/1.3/' + JSON.stringify([view.spreadsheet_id || '',view.series.id,view.episode.id]) : '';
  let memory = {shot:null,notes:{},drafts:{},positions:{}};
  let disk = Boolean(storageKey);
  if (storageKey) {
    try {
      const data = JSON.parse(localStorage.getItem(storageKey) || '{}');
      if (data && typeof data === 'object') {
        for (const key of ['notes','drafts','positions']) if (data[key] && typeof data[key] === 'object' && !Array.isArray(data[key])) memory[key]=data[key];
        if (selectedShot(data.shot)) memory.shot=data.shot;
      }
    } catch { disk=false; }
  }
  function remember() {
    if (!storageKey) return false;
    try { localStorage.setItem(storageKey,JSON.stringify(memory)); disk=true; return true; }
    catch { disk=false; return false; }
  }
  function tag(parent,name,content,cls) {
    const el=document.createElement(name);
    if (content!==undefined) el.textContent=content;
    if (cls) el.className=cls;
    parent.append(el);
    return el;
  }
  function link(parent,label,url,cls='action') {
    const el=tag(parent,'a',label,cls); el.href=url; return el;
  }
  function button(parent,label,fn,cls) {
    const el=tag(parent,'button',label,cls); el.type='button'; el.onclick=fn; return el;
  }
  function heading(title,context) {
    if(context) tag(host,'p',context,'eyeline');
    tag(host,'h1',title);
  }
  function date(text) {
    const time=new Date(text);
    return Number.isNaN(time.valueOf()) ? 'horário indisponível' : time.toLocaleString('pt-BR',{dateStyle:'short',timeStyle:'short'});
  }
  function rows(name) { return ready && Array.isArray(view[name]) ? view[name] : []; }
  function imgPath(value) {
    if (typeof value!=='string' || !value || /[\x00-\x1F\\]/.test(value)) return '';
    if (/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+$/i.test(value)) return value;
    if (/^[a-z][a-z\d+.-]*:|^\//i.test(value)) return '';
    return value;
  }
  function frame(parent,shot,hero=false) {
    const src=imgPath(shot.thumbnail);
    const placeholder=()=>tag(parent,'span','Quadro indisponível','unavailable');
    if(!src) { placeholder(); return; }
    const i=tag(parent,'img',undefined,hero?'keyframe':'');
    i.alt=hero ? 'Quadro de referência de '+(shot.label || shot.id) : '';
    i.onerror=()=>{i.remove();placeholder();}; i.src=src;
  }
  function queuePending(item) {return ['PROPOSTA','EM REVISÃO','CONFLITO','PENDENTE','PROPOSTA REGISTRADA'].includes(String(item.status||'').toUpperCase());}
  function pending(){return rows('queue').filter(queuePending);}
  function openPair(){return rows('pairs').find(p=>p.manifest?.pair_id && !p.unavailable &&
    !(selectedShot(p.shot_id)?.preferences||[]).some(pref=>pref.pair_id===p.manifest.pair_id&&pref.confirmed));}
  function defaultShot(){return selectedShot(memory.shot) || selectedShot(pending()[0]?.shot_id) || selectedShot(openPair()?.shot_id) || shots[0];}
  function shotHref(id){return '#plano='+encodeURIComponent(id);}
  function pairHref(shot,pair) {
    if(pair && rows('pairs').length===1) return 'takes.html';
    const p=new URLSearchParams();
    if(pair?.manifest?.pair_id) p.set('pair',pair.manifest.pair_id);
    if(shot) p.set('shot',shot.id);
    return 'takes.html'+(p.size?'?'+p:'');
  }
  function actionLinks(parent,shot){
    const actions=tag(parent,'div',undefined,'actions');
    link(actions,'Tenho um roteiro','#roteiro');
    link(actions,'Quero revisar uma cena','#planos');
    link(actions,'Tenho dois takes','#takes');
  }
  function emptyHome(){
    const hero=tag(host,'div',undefined,'hero');
    const left=tag(hero,'div');tag(left,'p','Cinematic Production Engine','eyeline');
    tag(left,'h1','Mesa de direção');
    tag(left,'p','Peça “abre meu episódio” na conversa. O agente prepara a mesa com os planos e as decisões da sua produção.');
    link(left,'Abrir decisões no Sheets',document.getElementById('sheetLink').href,'action primary');
    const figure=tag(hero,'figure');
    frame(figure,{thumbnail:'../examples/series-worked/frames/P06.png',label:'A última água · SH06'},true);
    tag(figure,'figcaption','A última água · prévia esquemática do estudo de direção');
    const section=tag(host,'section');tag(section,'h2','Escolher material');actionLinks(section);
  }
  function home(){
    if(!ready) {emptyHome();return;}
    const shot=defaultShot(), next=pending()[0], pair=openPair();
    const hero=tag(host,'div',undefined,'hero'+(shot?'':' without-image'));
    const left=tag(hero,'div');
    tag(left,'p',[view.series.is_test?'Ensaio':null,view.series.name,'Episódio '+view.episode.number].filter(Boolean).join('   /   '),'eyeline');
    tag(left,'h1',view.episode.title || 'Continuar episódio');
    if(shot) tag(left,'p',(memory.shot?'Último plano trabalhado · ':'Plano de entrada · ')+shotName(shot),'lead');
    const action=tag(left,'div',undefined,'actions');
    link(action,'Continuar episódio',shot?shotHref(shot.id):'#roteiro','action primary');
    link(action,'Ver decisões','#fila');
    const fresh=tag(left,'div',undefined,'read-time');tag(fresh,'span','Leitura do Sheets · '+date(view.read_at),'caption');
    button(fresh,'Recarregar mesa',()=>location.reload(),'text-button');
    if(shot){
      const fig=tag(hero,'figure');frame(fig,shot,true);
      tag(fig,'figcaption',[shot.scene,shotName(shot),shot.duration_s!==undefined?shot.duration_s+' s':null].filter(Boolean).join(' · '));
    }
    const panel=tag(host,'section',undefined,'paper');
    tag(panel,'h2','Próxima decisão');
    if(next) {
      tag(panel,'p',next.title || next.request || next.summary || next.id,'lead');
      const target=selectedShot(next.shot_id);
      if(target)link(panel,'Revisar '+shotName(target),shotHref(target.id));
      else link(panel,'Abrir a fila','#fila');
    } else if(pair){
      const target=selectedShot(pair.shot_id);
      const label=target?shotName(target):'plano';
      tag(panel,'p',pair.manifest.question||'Escolher o take de '+label,'lead');
      link(panel,'Ouvir o par de '+label,pairHref(target,pair));
    } else {
      tag(panel,'p','Nenhuma proposta pendente nesta leitura.');
      const gate=rows('workflow').find(w=>w.status==='IN_PROGRESS') || rows('workflow').find(w=>w.status==='REVIEW_REQUIRED');
      if(gate)tag(panel,'p','Etapa em andamento · '+gate.name,'caption');
    }
    const paths=tag(host,'section');tag(paths,'h2','Começar pelo material');actionLinks(paths,shot);
  }
  function details(parent,label) {
    const d=tag(parent,'details');tag(d,'summary',label);return d;
  }
  function provenance(parent,source) {
    if(!source?.id) {tag(parent,'p','Decisão de origem ainda não registrada.','caption');return;}
    const d=details(parent,'Decisão '+source.id+' · revisão '+source.revision);
    if(source.reason || source.rationale)tag(d,'p',source.reason || source.rationale);
    if(/^https:\/\/docs\.google\.com\/spreadsheets\/d\/[\w-]+\/edit(?:[?#][^\s]*)?$/.test(source.sheet_url || '')){
      const a=link(d,'Localizar no Sheets',source.sheet_url);a.target='_blank';a.rel='noopener';
    }
  }
  function formatted(value){
    if(value==null || value==='')return 'Ainda sem registro';
    if(Array.isArray(value))return value.map(formatted).join(' · ');
    if(typeof value==='object')return Object.entries(value).map(([k,v])=>k+' · '+formatted(v)).join('\n');
    const word=String(value);
    const hand=/^([\p{L} -]+)\.(esquerda|direita)$/iu.exec(word);
    return hand?'mão '+hand[2].toLowerCase()+' de '+hand[1]:word.replaceAll('_',' ');
  }
  function brief(parent,pairs){
    const dl=tag(parent,'dl',undefined,'brief');
    for(const [name,val] of pairs) {tag(dl,'dt',name);tag(dl,'dd',formatted(val));}
  }
  function filmstrip(active){
    const nav=tag(host,'nav',undefined,'filmstrip');nav.setAttribute('aria-label','Sequência de planos');
    for(const shot of shots){
      const a=link(nav,'',shotHref(shot.id),'frame');
      a.setAttribute('aria-label',[shot.id,shot.label,shot.scene].filter(Boolean).join(' · '));
      if(active?.id===shot.id) a.setAttribute('aria-current','true');
      frame(a,shot);tag(a,'span',shot.label || shot.id);
      if(active?.id===shot.id) requestAnimationFrame(()=>{nav.scrollLeft=Math.max(0,a.offsetLeft-nav.offsetLeft-nav.clientWidth/2+a.offsetWidth/2);});
    }
  }
  function plans(){
    heading('Planos da sequência',ready?view.episode.title:'Mesa de direção');
    if(!shots.length) {
      tag(host,'p',ready?'Este episódio ainda não tem decupagem.':'Abra um episódio na conversa ou consulte a decupagem do estudo.');
      link(host,'Consultar roteiro','#roteiro');
      if(!ready)link(host,'Ver estudo de seis planos','../examples/series-worked/episode-guide.html');
      return;
    }
    const scenes=[...new Set(shots.map(s=>s.scene).filter(Boolean))];
    const filter=tag(host,'label',undefined,'field');tag(filter,'span','Cena');
    const select=tag(filter,'select');tag(select,'option','Todas as cenas').value='';
    for(const scene of scenes)tag(select,'option',scene).value=scene;
    filmstrip();
    const list=tag(host,'div',undefined,'plan-list');
    function show(){list.replaceChildren();
      for(const s of shots.filter(s=>!select.value || s.scene===select.value)){
        const a=link(list,'',shotHref(s.id),'plan-line');
        tag(a,'strong',s.label||s.id);tag(a,'span',s.intention || s.action || s.scene);tag(a,'small',Number(s.duration_s)+' s');
      }
    }
    select.onchange=show;show();
  }
  function note(parent,key,signature,label='Notas de direção'){
    const id='note-'+key, existing=memory.notes[key], rev=signature || '';
    const wrap=tag(parent,'div',undefined,'note-box');
    const l=tag(wrap,'label',label);l.htmlFor=id;
    const input=tag(wrap,'textarea',undefined,'note');input.id=id;input.value=typeof existing?.text==='string'?existing.text:'';
    const state=tag(wrap,'p',existing?.text?(disk?'Rascunho local recuperado.':'Rascunho disponível nesta sessão.'):'Rascunho local · somente neste dispositivo.','caption');
    state.setAttribute('role','status');
    const changed=existing?.text && existing.base && existing.base!==rev;
    if(changed)tag(wrap,'p','A versão do material mudou. Confira o conteúdo antes de reutilizar sua anotação.','warn');
    input.oninput=()=>{
      memory.notes[key]={text:input.value,base:rev};
      state.textContent=remember()?'Rascunho salvo neste dispositivo.':'Não foi possível salvar neste navegador. Conserve o texto antes de sair.';
    };
  }
  function showPairActions(parent,shot){
    const pairs=rows('pairs').filter(p=>p.shot_id===shot.id && p.manifest?.pair_id);
    if(!pairs.length){
      tag(parent,'p','Nenhum par apresentado para este plano. Peça “compare dois takes deste plano” na conversa.','caption');
      return;
    }
    for(const [i,p] of pairs.entries()){
      if(p.unavailable){tag(parent,'p','Par indisponível · '+p.unavailable,'warn');continue;}
      link(parent,pairs.length===1?'Comparar takes':'Comparar par '+(i+1),pairHref(shot,p),'action primary');
    }
  }
  function showPreferences(parent,shot){
    const preferences=shot.preferences||[];
    if(!preferences.length)return;
    const group=tag(parent,'section',undefined,'preference');tag(group,'h2','Preferências de direção');
    const secs=value=>Number.isFinite(value)?(value/1000).toLocaleString('pt-BR',{maximumFractionDigits:3})+' s':'';
    const choices={A:'Take A',B:'Take B',TIE:'Empate',BOTH_FAIL:'Ambos rejeitados'};
    const scopes={deliverable:'este material',scene:'esta cena',episode:'este episódio',project:'esta série'};
    for(const f of preferences){
      const item=tag(group,'div',undefined,'entry');
      tag(item,'strong',[choices[f.choice]||f.choice,secs(f.mark_ms)].filter(Boolean).join(' · '));
      if(f.reason)tag(item,'p',f.reason);
      tag(item,'p',(f.confirmed?'Decisão confirmada por releitura':'Histórico pendente de confirmação')+' · '+(scopes[f.scope]||f.scope||'escopo sem indicação'),'caption');
      if(f.current===false)tag(item,'p','Referente à versão apresentada anteriormente.','warn');
      const d=details(item,'Trecho e versões assistidas');
      if(Number.isFinite(f.start_ms)&&Number.isFinite(f.end_ms))tag(d,'p',secs(f.start_ms)+' a '+secs(f.end_ms));
      for(const [side,t] of Object.entries(f.takes||{}))tag(d,'p',side+' · '+t.id+' · versão '+t.version+' · revisão '+t.revision);
      if(f.shot_revision)tag(d,'p','Plano na revisão '+f.shot_revision);
      if(f.source)provenance(d,f.source);
    }
  }
  const factLabels={character_knowledge:'Personagens',audience_knowledge:'Público',relationship:'Relações',prop:'Objetos',location:'Locações',open_question:'Perguntas em aberto'};
  function factsAt(entries,episode,limit){
    return (entries||[]).filter(f=>f.episode_number<episode || f.episode_number===episode && f.sequence<=limit)
      .sort((a,b)=>a.episode_number-b.episode_number || a.sequence-b.sequence);
  }
  function timePoints(shot){
    const exact=shot?.temporal || {};
    const previous=Number.isSafeInteger(exact.previous_sequence)?exact.previous_sequence:0;
    const points=[{value:previous,label:exact.precision==='episode' || !shot?.temporal?'Na abertura do episódio':exact.precision==='scene'?'Antes do primeiro fato desta cena':'Antes do primeiro fato deste plano'}];
    for(const p of exact.positions||[]){
      if(Number.isSafeInteger(p.sequence) && !points.some(x=>x.value===p.sequence)) points.push({value:p.sequence,label:(p.beat || 'Momento registrado')+' · posição '+p.sequence});
    }
    return points;
  }
  const nameKey=name=>String(name).normalize('NFC').trim().toLocaleUpperCase('pt-BR');
  function bible(parent,shot,speaker=''){
    const data=view.bible || {}, pts=timePoints(shot);
    if(!speaker)tag(parent,'h2','Bíblia na cena');
    if(shot && (shot.temporal?.precision==='episode'||!shot.temporal))tag(parent,'p','A fala ainda não tem posição verificada. A consulta começa na abertura do episódio.','caption');
    if(shot?.temporal?.precision==='scene')tag(parent,'p','Os fatos estão localizados por cena. Selecione o momento registrado que corresponde à fala.','caption');
    const label=tag(parent,'label',undefined,'field');tag(label,'span','Momento da história');
    const select=tag(label,'select');
    for(const pt of pts){const opt=tag(select,'option',pt.label);opt.value=String(pt.value);}
    const chosen=!speaker && pts.find(p=>p.value===memory.positions[shot.id]);select.value=String(chosen?.value??pts[0].value);
    const box=tag(parent,'div');let filter=speaker;
    function display(){
      box.replaceChildren();
      const limit=Number(select.value), all=factsAt(data.timeline,view.episode.number,limit);
      const known=new Map();
      for(const f of all)known.set(JSON.stringify([f.kind,f.subject,f.key]),f);
      const facts=[...known.values()];
      const subjects=[...new Set(facts.filter(f=>f.kind!=='audience_knowledge').map(f=>f.subject))];
      if(!speaker){
        if(!subjects.includes(filter))filter='';
        const acts=tag(box,'div',undefined,'actions');acts.setAttribute('aria-label','Consultar entidade');
        for(const s of ['',...subjects]){
          const b=button(acts,s || 'Todos',()=>{filter=s;display();});b.setAttribute('aria-pressed',String(filter===s));
        }
      }
      const inScope=f=>!filter || nameKey(f.subject)===nameKey(filter);
      if(speaker && !facts.some(f=>f.kind==='character_knowledge' && inScope(f)))tag(box,'p','Conhecimento de '+speaker+' desconhecido neste ponto.');
      for(const [kind,title] of Object.entries(factLabels)){
        const selected=facts.filter(f=>f.kind===kind && (inScope(f) || kind==='audience_knowledge'));
        if(!selected.length)continue;
        const group=tag(box,'div',undefined,'entry');tag(group,'h3',title);
        for(const f of selected){
          const who=kind==='audience_knowledge'?'Público':f.subject;
          tag(group,'p',who+' · '+f.key+' · '+f.value);
          const prev=f.previous_decision_id && all.find(p=>p.source?.id===f.previous_decision_id);
          if(prev)tag(group,'p','Antes · '+prev.value,'caption');
          tag(group,'small','EP'+f.episode_number+' · '+f.beat,'caption');
          provenance(group,f.source);
        }
      }
      if(!facts.length && !speaker)tag(box,'p','Conhecimento desconhecido neste ponto. Ainda não há fato registrado.');
      const proposals=factsAt(data.proposals,view.episode.number,limit).filter(inScope);
      if(proposals.length){
        const group=details(box,'Hipóteses em revisão ('+proposals.length+')');
        for(const f of proposals){tag(group,'p',f.subject+' · '+f.key+' · '+f.value);provenance(group,f.source);}
      }
      const check=details(box,'Conferir uma fala com o que já foi estabelecido');
      const fields=tag(check,'div',undefined,'actions');
      const holder=tag(fields,'input');holder.placeholder='Personagem';holder.setAttribute('aria-label','Personagem');holder.value=filter;
      const key=tag(fields,'input');key.placeholder='Assunto';key.setAttribute('aria-label','Assunto');
      const claim=tag(fields,'input');claim.placeholder='Informação pressuposta na fala';claim.setAttribute('aria-label','Informação pressuposta');
      const result=tag(check,'div');result.setAttribute('aria-live','polite');
      button(check,'Conferir informação',()=>{
        result.replaceChildren();const norm=s=>String(s).trim().toLocaleLowerCase('pt-BR');
        if(![holder.value,key.value,claim.value].every(v=>v.trim())){tag(result,'p','Informe o personagem, o assunto e o que a fala pressupõe.');return;}
        const f=facts.find(x=>x.kind==='character_knowledge' && norm(x.subject)===norm(holder.value) && norm(x.key)===norm(key.value));
        if(!f){tag(result,'p','Desconhecido neste ponto.');return;}
        tag(result,'p',(norm(f.value)===norm(claim.value)?'Coincide com o fato registrado.':'Diverge do fato registrado: '+f.value)+ ' A interpretação da fala cabe à direção.');
        provenance(result,f.source);
      });
    }
    select.onchange=()=>{if(!speaker){memory.positions[shot.id]=Number(select.value);remember();}display();};
    display();
  }
  function shotPage(shot){
    if(!shot){plans();return;}
    memory.shot=shot.id;remember();
    link(host,'← Sequência','#planos','return-link');
    heading(shot.scene || shot.label || shot.id,[shot.label || shot.id,'rev. '+shot.revision,shot.duration_s+' s'].filter(Boolean).join('   /   '));
    filmstrip(shot);
    const hero=tag(host,'div',undefined,'hero shot-hero');const fig=tag(hero,'figure');frame(fig,shot,true);
    tag(fig,'figcaption',!shot.thumbnail && shot.presentation?shot.presentation:shot.intention || shot.scene || shot.id);
    const summary=tag(hero,'div',undefined,'shot-summary');
    brief(summary,[['Ação',shot.action],['Câmera',shot.camera],['Som',shot.sound],['Take escolhido',shot.selected_take?.label || shot.selected_take?.id || 'Em aberto']]);
    showPairActions(summary,shot);
    const places=tag(host,'div',undefined,'columns');
    const continuity=tag(places,'section');tag(continuity,'h2','Continuidade do corte');
    const previous=shots.slice(0,shots.indexOf(shot)).reverse().find(s=>s.scene===shot.scene);
    const label=shotName(shot);
    brief(continuity,[[previous?'Saída de '+shotName(previous):'Primeiro plano da cena',previous?.states?.out || 'Início da sequência'],['Entrada de '+label,shot.states?.in],['Saída de '+label,shot.states?.out]]);
    for(const w of shot.continuity_review || []){
      const d=details(continuity,'Conferir '+w.field+' · '+w.before+' → '+w.after);
      const sources=w.decisions || [w.decision || w.source || w.exception?.decision].filter(Boolean);
      if(sources.length){tag(d,'p',w.status==='JUSTIFIED'?'Exceção justificada pela direção.':'Decisões relacionadas.');for(const src of sources)provenance(d,src);}
      else tag(d,'p','A divergência ainda precisa de decisão. Na conversa, peça correção, justifique uma exceção ou deixe pendente.');
    }
    const related=details(continuity,'Materiais e decisões relacionados');
    for(const l of shot.links || [])tag(related,'p',l.relation+' · '+l.from.id+' → '+l.to.id+(l.stale?' · rever versão':''));
    if(shot.last_decision)provenance(related,shot.last_decision);
    const dependencies=shot.impact?.affected || shot.impact || [];
    if(Array.isArray(dependencies)) for(const item of dependencies) tag(related,'p','Afetado · '+(item.current?.id||item.id)+' · '+(item.relationship || ''));
    const notes=tag(places,'section',undefined,'paper');tag(notes,'h2','Caderno do plano');
    note(notes,shot.id,JSON.stringify([shot.revision,shot.selected_take?.sha256,shot.states]));
    showPreferences(host,shot);
    const b=tag(host,'section');bible(b,shot);
    const alternatives=rows('alternatives').filter(a=>a.shot_id===shot.id);
    const alt=tag(host,'section');tag(alt,'h2','Alternativas de montagem');
    if(alternatives.length)items(alt,alternatives);else tag(alt,'p','Nenhuma alternativa registrada para este plano.');
    tag(alt,'p','Para experimentar uma variação, descreva na conversa o plano e a mudança desejada.','caption');
  }
  function items(parent,data){
    const ul=tag(parent,'ul',undefined,'decision-list');
    for(const q of data){
      const li=tag(ul,'li');tag(li,'strong',q.title || q.request || q.id);
      tag(li,'p',q.status || 'Estado desconhecido','status');
      if(q.summary || q.request)tag(li,'p',q.summary || q.request);
      if(q.actor)tag(li,'p',q.actor,'caption');
      if(q.reason)tag(li,'p','Motivo · '+q.reason);
      const shot=selectedShot(q.shot_id);
      if(shot)link(li,shotName(shot),shotHref(shot.id));
      if(q.source?.id)provenance(li,q.source);
      if(Number.isInteger(q.source?.row)&&q.source.row>1&&/^https:\/\/docs\.google\.com\/spreadsheets\/d\/[\w-]+\/edit#gid=\d+$/.test(view.queue_url||'')){
        const a=link(li,'Localizar proposta no Sheets',view.queue_url+'&range=A'+q.source.row);
        a.target='_blank';a.rel='noopener';
      }
      if(q.receipt)tag(li,'p','Recibo · '+formatted(q.receipt),'caption');
    }
  }
  function queue(){
    heading('Decisões do episódio',ready?view.episode.title:'Mesa de direção');
    if(rows('queue').length)items(host,rows('queue'));else tag(host,'p','Nenhuma proposta na leitura disponível.');
    const dashboard=view?.queue_url || view?.dashboard_url;
    const url=/^https:\/\/docs\.google\.com\/spreadsheets\/d\/[\w-]+\/edit(?:[?#][^\s]*)?$/.test(dashboard||'')?dashboard:document.getElementById('sheetLink').href;
    link(host,'Abrir fila no Sheets',url,'action primary');
    tag(host,'p','Deixe uma proposta na planilha e peça “revise as pendências” na conversa.','caption');
  }
  // Keep original line breaks and cue spelling, including Fountain's @, (V.O.) and ^.
  function speakerCue(line,next,cast){
    const colon=line.indexOf(':'), head=colon<0?line:line.slice(0,colon);
    if(head.length>160)return null;
    const cueText=head.trimEnd().replace(/\^$/,'').trimEnd().replace(/\([^()]*\)$/,'').trimEnd();
    const match=/^([ \t]*@?)([\p{L}][\p{L}\p{M}\p{N} '’.-]*)$/u.exec(cueText);
    if(!match)return null;
    const [,prefix,name]=match, known=cast.get(nameKey(name)), forced=prefix.endsWith('@');
    if(!known && !forced)return null;
    if(colon<0 && (!next?.trim() || (!forced && name!==name.toLocaleUpperCase('pt-BR'))))return null;
    const dialogue=colon<0?next:line.slice(colon+1);
    return {prefix,name,remaining:line.slice(prefix.length+name.length),speaker:known || name,dialogue:dialogue?.trim()};
  }
  function screenplay(parent,content,panelId){
    const pre=tag(parent,'pre',undefined,'screenplay');
    if(!ready){pre.textContent=content;return;}
    const cast=new Map();
    for(const ch of view.materials?.Characters || [])if(ch.name)cast.set(nameKey(ch.name),ch.name);
    for(const f of [...(view.bible?.timeline || []),...(view.bible?.proposals || [])]){
      if(f.kind==='character_knowledge' && f.subject && !cast.has(nameKey(f.subject)))cast.set(nameKey(f.subject),f.subject);
    }
    const lines=content.split(/(\r\n|\r|\n)/);
    const sheet=tag(parent,'section',undefined,'speaker-sheet');
    sheet.hidden=true;sheet.id=panelId;
    let active=null;
    function close(){
      sheet.hidden=true;sheet.replaceChildren();
      if(active){active.setAttribute('aria-expanded','false');active.focus();active=null;}
    }
    function consult(cue,trigger){
      if(active===trigger){close();return;}
      active?.setAttribute('aria-expanded','false');active=trigger;trigger.setAttribute('aria-expanded','true');
      sheet.hidden=false;sheet.replaceChildren();
      const title=tag(sheet,'h2','Bíblia de '+cue.speaker);title.id=panelId+'-title';
      sheet.setAttribute('aria-labelledby',title.id);
      if(cue.dialogue)tag(sheet,'blockquote',cue.dialogue);
      tag(sheet,'p','Esta fala não tem posição narrativa verificada. A ficha abre com o que já estava estabelecido na abertura do episódio.','caption');
      button(sheet,'Voltar à fala',close,'text-button');
      const label=tag(sheet,'label',undefined,'field');tag(label,'span','Plano ou cena de referência');
      const pick=tag(label,'select');pick.setAttribute('aria-label','Plano ou cena de referência');
      tag(pick,'option','Abertura do episódio').value='';
      for(const shot of shots)tag(pick,'option',[shotName(shot),shot.scene].filter(Boolean).join(' · ')).value=shot.id;
      const facts=tag(sheet,'div',undefined,'speaker-facts');
      function show(){facts.replaceChildren();bible(facts,selectedShot(pick.value),cue.speaker);}
      pick.onchange=show;show();
      title.tabIndex=-1;title.focus();
    }
    let plain='';
    for(let i=0;i<lines.length;i+=2){
      const line=lines[i],end=lines[i+1] || '',cue=speakerCue(line,lines[i+2],cast);
      if(!cue){plain+=line+end;continue;}
      plain+=cue.prefix;
      if(plain)tag(pre,'span',plain);
      const trigger=button(pre,cue.name,()=>consult(cue,trigger),'character-cue');
      trigger.setAttribute('aria-label','Consultar '+cue.speaker+' na bíblia desta fala');
      trigger.setAttribute('aria-controls',panelId);trigger.setAttribute('aria-expanded','false');
      plain=cue.remaining+end;
    }
    if(plain)tag(pre,'span',plain);
  }
  function script(){
    heading('Mesa de roteiro',ready?view.episode.title:'Entrada por material');
    const scripts=ready ? (view.materials?.Screenplays || view.screenplays || []) : [];
    for(const [idx,row] of scripts.entries()){
      const d=details(host,(row.label || row.title || row.id)+' · rev. '+row.revision);
      const text=row.text_or_ref || row.screenplay || row.screenplay_text || row.text || row.content || row.script_text || row.synopsis || row.excerpt;
      if(text) screenplay(d,String(text),'script-bible-'+idx);else tag(d,'p','Peça ao agente para abrir o texto desta versão na conversa.');
    }
    const open=tag(host,'label',undefined,'field');tag(open,'span','Ler um roteiro local em texto');
    const picker=tag(open,'input');picker.type='file';picker.accept='.txt,.md,.fountain';
    const preview=tag(host,'div');
    picker.onchange=async()=>{const f=picker.files[0];if(!f)return;
      if(f.size>2000000){preview.replaceChildren();tag(preview,'p','Escolha um trecho de até 2 MB para esta leitura.');return;}
      try{
        const content=await f.text();
        if(picker.files[0]!==f)return;
        preview.replaceChildren();screenplay(preview,content,'local-script-bible');
      }catch{if(picker.files[0]===f){preview.replaceChildren();tag(preview,'p','Não foi possível ler este arquivo.');}}
    };
    tag(host,'p','Para integrar uma versão à produção, indique o roteiro ao agente na conversa.','caption');
    if(ready)note(host,'$roteiro',String(scripts[0]?.revision||''),'Notas de roteiro');
  }
  function takes(){
    heading('Comparar takes',ready?view.episode.title:'Entrada por material');
    const pairs=rows('pairs');
    for(const [i,p] of pairs.entries()) {
      const section=tag(host,'section');tag(section,'h2',p.manifest?.question || 'Comparação '+(i+1));
      const shot=selectedShot(p.shot_id);
      if(shot)tag(section,'p',[shot.id,shot.scene].filter(Boolean).join(' · '));
      link(section,'Abrir este par',pairHref(shot,p),'action primary');
    }
    if(!pairs.length)tag(host,'p','Abra dois arquivos locais para assistir e experimentar. Para registrar uma preferência, peça ao agente que apresente esse par no episódio.');
    link(host,pairs.length?'Explorar outros arquivos':'Explorar dois arquivos',pairHref(null,null),'action primary');
  }
  function navigate(){
    if(typeof invalidatePrepared==='function')invalidatePrepared(true);
    const raw=location.hash.slice(1) || 'inicio';
    const workshop=raw==='oficina';
    host.hidden=workshop;document.getElementById('advanced').hidden=!workshop;
    for(const a of document.querySelectorAll('.masthead nav a')){
      const match=a.getAttribute('href')==='#'+(raw.startsWith('plano=')?'planos':raw);
      if(match)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
    }
    if(workshop)return;
    host.replaceChildren();
    if(raw.startsWith('plano=')){let id='';try{id=decodeURIComponent(raw.slice(6));}catch{} shotPage(selectedShot(id));}
    else ({inicio:home,planos:plans,fila:queue,roteiro:script,takes}[raw] || home)();
    if(!disk && ready)tag(host,'p','Armazenamento local indisponível. Suas anotações podem durar apenas esta sessão.','warn');
  }
  window.addEventListener('hashchange',()=>{
    navigate();
    const title=(host.hidden?document.getElementById('advanced'):host).querySelector?.('h1');
    if(title){title.tabIndex=-1;title.focus({preventScroll:true});}
    window.scrollTo?.(0,0);
  });
  navigate();
})();
