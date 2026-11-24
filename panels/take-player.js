'use strict';
const el = id => document.getElementById(id);
const labels = ['A','B'];
const files = new Map(), players = new Map(), urls = [];
let manifest = null, current = 0, commonEnd = 0, segment = {}, frame = 0, generation = 0;
let isPlaying = false, demo = false, playSequence = 0;
let looping = false, activeDeskPair = null;
const sidecarLoads = new Map();
const format = ms => (ms / 1000).toLocaleString('pt-BR', {minimumFractionDigits:3,maximumFractionDigits:3}) + ' s';
function notify(message) { el('status').textContent = message; }
function clearMessage() { el('copy').disabled = true; el('out').value=''; el('out').hidden=true; }
function canonical(value) {
 if (Array.isArray(value)) return value.map(canonical);
 if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])]));
 return value;
}
async function sha(bytes) {
 const result=await crypto.subtle.digest('SHA-256',bytes);
 return [...new Uint8Array(result)].map(n=>n.toString(16).padStart(2,'0')).join('');
}
function stop() {
 isPlaying=false;playSequence++;cancelAnimationFrame(frame);
 for (const player of players.values()) if(player.pause)player.pause();
}
function reset() {
 remember();
 generation++;stop();
 for(const url of urls)URL.revokeObjectURL(url);urls.length=0;players.clear();files.clear();
 for(const label of labels)el('slot-'+label).replaceChildren();
 manifest=null;activeDeskPair=null;demo=false;segment={};current=0;commonEnd=0;looping=false;clearMessage();renderLoop();
 el('choice').value='';el('scope').value='deliverable';el('reason').value='';el('authorize').checked=false;
 el('question').textContent='Carregue o par e os dois arquivos de mídia.';el('clock').textContent=format(0);
 el('segment').textContent='Escolha um instante ou um trecho.';el('seek').max='0';el('seek').value='0';
 for(const id of ['play','pause','seek','swap','start','mark','end','go-time'])el(id).disabled=true;
 el('loop-band').hidden=true;el('marker-pin').hidden=true;el('time-entry').value='';
}
function sound() {
 for(const [label,player] of players)if('muted' in player)player.muted=el('sound').value!==label;
}
function seek(ms) {
 current=Math.max(0,Math.min(commonEnd,Math.round(ms)));
 for(const player of players.values())if('currentTime' in player)player.currentTime=current/1000;
 updateClock();
}
function updateClock() { el('clock').textContent=format(current)+' / '+format(commonEnd);el('seek').value=String(current); }
function tick() {
 if(!isPlaying)return;
 const tracks=[...players.values()].filter(p=>'currentTime' in p);
 if(!tracks.length)return;
 const audible=players.get(el('sound').value);
 const primary=audible&&'currentTime'in audible?audible:tracks[0];
 current=Math.min(commonEnd,Math.round(primary.currentTime*1000));
 if(looping&&validLoop()&&(current>=segment.end_ms||current<segment.start_ms||tracks.some(p=>p.ended))){
  seek(segment.start_ms);
  if(tracks.some(p=>p.paused||p.ended)){void play();return;}
  frame=requestAnimationFrame(tick);return;
 }
 if(current>=commonEnd||tracks.some(p=>p.ended)){stop();seek(commonEnd);return;}
 for(const player of tracks)if(player!==primary&&Math.abs(player.currentTime-primary.currentTime)>0.09)player.currentTime=primary.currentTime;
 updateClock();frame=requestAnimationFrame(tick);
}
async function play() {
 if(players.size!==2||!commonEnd)return;
 if(looping&&validLoop()&&(current<segment.start_ms||current>=segment.end_ms))seek(segment.start_ms);
 else if(current>=commonEnd)seek(0);
 stop();const playToken=playSequence;
 try{
  await Promise.all([...players.values()].filter(p=>p.play).map(p=>p.play()));
  if(playToken!==playSequence)return;
  isPlaying=true;tick();
 }catch(e){if(playToken===playSequence){stop();notify('Não foi possível reproduzir este formato no navegador. '+e.message);}}
}
async function loadManifest(data) {
 reset();const token=generation;const {pair_sha256:checksum,...body}=data;
 if(body.kind!=='CPE_TAKE_PAIR_1'||!body.pair_id||!body.project_id||!body.episode_id||
    !body.takes?.A||!body.takes?.B||body.takes.A.id===body.takes.B.id||
    body.takes.A.sha256===body.takes.B.sha256||
    !labels.every(l=>Number.isSafeInteger(body.takes[l].duration_ms)&&body.takes[l].duration_ms>=0&&
       /^(image|video|audio)\//.test(body.takes[l].mime)))throw Error('Par incompatível ou incompleto.');
 const digest=await sha(new TextEncoder().encode(JSON.stringify(canonical(body))));
 if(token!==generation)return false;
 if(checksum!==digest)throw Error('O manifesto foi alterado. Peça o par original.');
 manifest=data;
 const durations=labels.map(l=>body.takes[l].duration_ms).filter(n=>n>0);
 commonEnd=durations.length?Math.min(...durations):0;
 el('question').textContent=data.question;el('seek').max=String(commonEnd);updateClock();return true;
}
async function loadMedia(blobs,token) {
 if(!manifest||blobs.length!==2)throw Error('Selecione os dois arquivos do par preparado.');
 const pair=manifest;const matches=new Map();
 for(const blob of blobs){
  const id=await sha(await blob.arrayBuffer());
  if(token!==generation)return;
  const label=labels.find(l=>pair.takes[l].sha256===id);
  if(!label||matches.has(label))throw Error('Os arquivos não correspondem às duas versões do par.');
  matches.set(label,blob);
 }
 for(const label of labels){
  const entry=pair.takes[label],kind=entry.mime.split('/')[0];const player=document.createElement(kind==='image'?'img':kind);
  player.setAttribute('aria-label','Take '+label);
  const url=URL.createObjectURL(new Blob([matches.get(label)],{type:entry.mime}));urls.push(url);
  const ready=kind==='image'?'load':'loadedmetadata';
  if(kind!=='image'){player.preload='auto';player.playsInline=true;}else player.alt='Take '+label;
  let timer;
  try{
   await new Promise((resolve,reject)=>{
    player.addEventListener(ready,resolve,{once:true});
    player.addEventListener('error',()=>reject(Error('O navegador não conseguiu abrir o take '+label+'.')),{once:true});
    timer=setTimeout(()=>reject(Error('Tempo de leitura da mídia esgotado.')),20000);player.src=url;
   });
  }catch(error){if(token!==generation)return;throw error;}
  finally{clearTimeout(timer);}
  if(token!==generation)return;
  if(kind!=='image'&&(!Number.isFinite(player.duration)||Math.abs(player.duration*1000-entry.duration_ms)>170))
   throw Error('A duração reconhecida pelo navegador diverge para o take '+label+'.');
  players.set(label,player);files.set(label,matches.get(label));el('slot-'+label).replaceChildren(player);
 }
 sound();seek(0);
 for(const id of ['seek','play','pause','go-time'])el(id).disabled=!commonEnd;
 for(const id of ['swap','mark','start','end'])el(id).disabled=false;
 notify(demo?'Estudo de demonstração. Qualquer voto gerado aqui ficará identificado como ensaio.':'Versões conferidas. Escolha o instante e registre o motivo.');
}
function marker(which) {
 if(players.size!==2)return;stop();
 if(which==='mark')segment.mark_ms=current;
 else segment[which+'_ms']=current;
 if(!validLoop())looping=false;
 drawMarkers();remember();clearMessage();
}
function validLoop(){
 return Number.isInteger(segment.start_ms)&&Number.isInteger(segment.end_ms)&&
        segment.start_ms>=0&&segment.start_ms<segment.end_ms&&segment.end_ms<=commonEnd;
}
function renderLoop(){
 const b=el('loop');b.disabled=!validLoop();b.setAttribute('aria-pressed',String(looping));
 b.textContent=looping?'↻ Repetição ativa':'↻ Repetir trecho';
}
function drawMarkers(){
 const v=n=>Number.isInteger(n)?format(n):'—';
 el('segment').textContent='Início '+v(segment.start_ms)+' · marca '+v(segment.mark_ms)+' · fim '+v(segment.end_ms);
 const band=el('loop-band'),pin=el('marker-pin');
 band.hidden=!validLoop();pin.hidden=!commonEnd||!Number.isInteger(segment.mark_ms);
 if(!band.hidden&&band.style){band.style.left=(100*segment.start_ms/commonEnd)+'%';band.style.width=(100*(segment.end_ms-segment.start_ms)/commonEnd)+'%';}
 if(!pin.hidden&&pin.style)pin.style.left=(100*segment.mark_ms/commonEnd)+'%';
 renderLoop();
}
function toggleLoop(){
 if(!validLoop())return;
 looping=!looping;renderLoop();remember();
 if(looping){seek(segment.start_ms);return play();}
}
function storageKey(){return activeDeskPair?'cpe.take.draft.1.'+activeDeskPair.manifest.pair_sha256:null;}
function remember(){
 const key=storageKey();if(!key)return;
 try{window.localStorage?.setItem(key,JSON.stringify({segment,current,looping,sound:el('sound').value,
   order:el('screens').firstElementChild===el('left')?'A':'B',scope:el('scope').value,choice:el('choice').value,reason:el('reason').value}));}
 catch{el('location').title='Este navegador não disponibilizou armazenamento local para as notas.';}
}
function restoreDeskDraft(){
 const key=storageKey();if(!key)return;
 let saved;
 try{saved=JSON.parse(window.localStorage?.getItem(key)||'null');}catch{return;}
 if(!saved||typeof saved!=='object')return;
 segment=Object.fromEntries(Object.entries(saved.segment||{}).filter(([k,v])=>['mark_ms','start_ms','end_ms'].includes(k)&&Number.isSafeInteger(v)&&v>=0&&v<=commonEnd));
 looping=saved.looping===true&&validLoop();drawMarkers();
 if(['A','B','mute'].includes(saved.sound)){el('sound').value=saved.sound;sound();}
 if(['','A','B','TIE','BOTH_FAIL'].includes(saved.choice))el('choice').value=saved.choice;
 if(['deliverable','scene','episode','project'].includes(saved.scope))el('scope').value=saved.scope;
 if(typeof saved.reason==='string')el('reason').value=saved.reason;
 if(saved.order==='A'||saved.order==='B'){const screens=el('screens'),first=saved.order==='A'?el('left'):el('right');if(screens.firstElementChild!==first)screens.insertBefore(first,screens.firstElementChild);}
 if(Number.isSafeInteger(saved.current))seek(saved.current);
 clearMessage();el('authorize').checked=false;
}
function makeVote() {
 if(!manifest||players.size!==2)throw Error('Carregue e confira os dois takes.');
 if(manifest.kind==='LOCAL_EXPLORATION')throw Error('Peça ao agente para vincular os dois arquivos ao plano antes de registrar uma decisão.');
 if(!el('authorize').checked)throw Error('Marque a autorização antes de preparar a mensagem.');
 if(!['A','B','TIE','BOTH_FAIL'].includes(el('choice').value))throw Error('Escolha explicitamente uma preferência.');
 const reason=el('reason').value.trim();if(!reason)throw Error('Registre o motivo da escolha.');
 const mark_ms=segment.mark_ms,start_ms=segment.start_ms??mark_ms,end_ms=segment.end_ms??mark_ms;
 if(![start_ms,mark_ms,end_ms].every(Number.isSafeInteger)||start_ms>mark_ms||mark_ms>end_ms||end_ms>commonEnd)
  throw Error('Marque um instante dentro do trecho selecionado.');
 return {kind:'CPE_TAKE_VOTE_1',pair_id:manifest.pair_id,pair_sha256:manifest.pair_sha256,
         choice:el('choice').value,preference_scope:el('scope').value,start_ms,mark_ms,end_ms,reason,
         authorized:true,demonstration:demo};
}
function blobFromChunks(chunks,mime){
 return new Blob(chunks.map(s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0))),{type:mime});
}
function sidecar(url,take){
 if(url!=='media/'+take.sha256+'.js'||!/^[a-f0-9]{64}$/.test(take.sha256))throw Error('Referência local de mídia inválida.');
 const existing=sidecarLoads.get(take.sha256);
 if(existing)return existing.promise;
 const pending={};sidecarLoads.set(take.sha256,pending);
 pending.promise=new Promise((resolve,reject)=>{
  const tag=document.createElement('script');let delivered=false;
  const finish=(fn,value)=>{sidecarLoads.delete(take.sha256);tag.remove();fn(value);};
  pending.accept=parts=>{try{const blob=blobFromChunks(parts,take.mime);delivered=true;finish(resolve,blob);}catch(err){finish(reject,err);}};
  tag.onerror=()=>finish(reject,Error('Arquivo de mídia da mesa indisponível.'));
  tag.onload=()=>{if(!delivered)finish(reject,Error('Verifique o conteúdo do arquivo da mesa.'));};
  tag.src=url;document.head.append(tag);
 });
 return pending.promise;
}
async function projectedBlob(url,take){
 const prefix='data:'+take.mime+';base64,';
 if(typeof url!=='string')throw Error('A mídia do par está indisponível.');
 if(url.startsWith(prefix))return blobFromChunks([url.slice(prefix.length)],take.mime);
 if(url==='media/'+take.sha256+'.js')return sidecar(url,take);
 throw Error('O par precisa de mídia local verificada.');
}
async function openDeskPair(item){
 if(!await loadManifest(item.manifest))return;
 const token=generation;
 try{
  const m=item.manifest,desk=window.CPE_DESK_DATA;
  if(m.episode_id!==desk.episode?.id||m.project_id!==desk.series?.id||m.shot?.id!==item.shot_id)throw Error('Par de outro episódio ou plano.');
  el('return').href='studio.html#plano='+encodeURIComponent(item.shot_id);
  el('location').textContent=desk.episode.title+' · '+item.shot_id;
  if(item.unavailable)throw Error(item.unavailable+' Peça uma nova apresentação ao agente para vincular o material disponível.');
  const blobs=await Promise.all(labels.map(l=>projectedBlob(item.media?.[l],m.takes[l])));
  if(token!==generation)return;
  await loadMedia(blobs,token);
  if(token!==generation)return;
  activeDeskPair=item;restoreDeskDraft();notify('Par da mesa conferido. Você pode assistir e comparar livremente.');
 }catch(err){if(token===generation){reset();notify(err.name==='RangeError'?'O navegador não conseguiu carregar este volume de mídia. Peça um recorte verificável ao agente.':err.message);}}
}
function conversationVote(vote){
 const selection={A:'o take A',B:'o take B',TIE:'empate',BOTH_FAIL:'rejeição dos dois takes'}[vote.choice];
 const scope={deliverable:'a estes takes',scene:'a esta cena',episode:'a este episódio',project:'à série'}[vote.preference_scope];
 const similar=(window.CPE_DESK_DATA?.pairs||[]).filter(p=>p.shot_id===activeDeskPair.shot_id&&p.manifest.question===manifest.question);
 const ref=similar.length>1?' (par '+manifest.pair_id.slice(-8)+')':'';
 return 'Registre '+selection+' no plano '+activeDeskPair.shot_id+' para a comparação “'+manifest.question+'”'+ref+'. Trecho de '+format(vote.start_ms)+' a '+format(vote.end_ms)+', marca '+format(vote.mark_ms)+'. Motivo: '+vote.reason+'. Aplicar '+scope+'.';
}
function setupDesk(){
 const desk=window.CPE_DESK_DATA;if(!desk?.episode)return;
 const params=new URLSearchParams(window.location?.search||''),shot=params.get('shot'),pair=params.get('pair');
 if(shot)el('return').href='studio.html#plano='+encodeURIComponent(shot);
 const entries=(desk.pairs||[]).filter(x=>!shot||x.shot_id===shot),sel=el('registered-pair');
 if(entries.length){
  const empty=document.createElement('option');empty.textContent='Selecionar comparação';empty.value='';sel.append(empty);
  for(const item of entries){const opt=document.createElement('option');opt.value=item.manifest.pair_id;opt.textContent=item.shot_id+' · '+item.manifest.question;sel.append(opt);}
  el('pair-picker').hidden=entries.length<2;
  sel.onchange=()=>{const item=entries.find(x=>x.manifest.pair_id===sel.value);if(item)return openDeskPair(item);reset();};
 }
 const selected=pair?entries.find(x=>x.manifest.pair_id===pair):entries.length===1?entries[0]:null;
 if(selected){sel.value=selected.manifest.pair_id;return openDeskPair(selected);}
 if(pair)notify('O par solicitado não está nesta leitura da mesa. Peça ao agente que confira as versões.');
}
async function previewDescriptor(file){
 const mime=file.type||'';
 if(!/^(image|video|audio)\//.test(mime))throw Error('O navegador não reconheceu o tipo deste arquivo.');
 const hash=await sha(await file.arrayBuffer());
 if(mime.startsWith('image/'))return {sha256:hash,mime,duration_ms:0};
 const player=document.createElement(mime.split('/')[0]),url=URL.createObjectURL(file);
 let timeout;
 try{
  player.preload='metadata';
  await new Promise((resolve,reject)=>{
   player.addEventListener('loadedmetadata',resolve,{once:true});
   player.addEventListener('error',()=>reject(Error('Formato de mídia indisponível neste navegador.')),{once:true});
   timeout=setTimeout(()=>reject(Error('Não foi possível ler a duração do arquivo.')),20000);
   player.src=url;
  });
  if(!Number.isFinite(player.duration)||player.duration<=0)throw Error('Não foi possível determinar a duração do take.');
  return {sha256:hash,mime,duration_ms:Math.floor(player.duration*1000)};
 }finally{clearTimeout(timeout);URL.revokeObjectURL(url);}
}
async function exploreFiles(blobs){
 reset();const token=generation;
 try{
  if(blobs.length!==2)throw Error('Selecione dois arquivos para explorar lado a lado.');
  const [a,b]=await Promise.all(blobs.map(previewDescriptor));
  if(token!==generation)return;
  if(a.sha256===b.sha256)throw Error('Os dois arquivos são idênticos.');
  manifest={kind:'LOCAL_EXPLORATION',takes:{A:a,B:b}};
  commonEnd=Math.min(...[a.duration_ms,b.duration_ms].filter(n=>n>0));
  if(!Number.isFinite(commonEnd))commonEnd=0;
  el('seek').max=String(commonEnd);el('location').textContent='Exploração local';
  el('question').textContent='A · '+(blobs[0].name||'primeiro arquivo')+'   /   B · '+(blobs[1].name||'segundo arquivo');
  await loadMedia(blobs,token);
  if(token!==generation)return;
  notify('Exploração local. Para guardar uma decisão, peça ao agente que apresente os takes neste plano.');
 }catch(err){if(token===generation){reset();notify(err.message);}}
}
function setup(){
 el('explore').onclick=()=>el('preview-files').click();
 el('preview-files').onchange=e=>{const files=Array.from(e.target.files);e.target.value='';if(files.length)return exploreFiles(files);};
 for(const d of window.CPE_TAKE_DEMOS??[]){const opt=document.createElement('option');opt.value=d.id;opt.textContent=d.title;el('example').append(opt);}
 el('manifest').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{await loadManifest(JSON.parse(await f.text()));notify('Selecione os arquivos dos dois takes.');}catch(err){notify(err.message);}e.target.value='';};
 el('clips').onchange=async e=>{
  const blobs=Array.from(e.target.files);e.target.value='';if(!blobs.length)return;
  if(!manifest){notify('Carregue o par primeiro.');return;}
  const previous=manifest;try{if(await loadManifest(previous))await loadMedia(blobs,generation);}catch(err){reset();notify(err.message);}
 };
 el('load-demo').onclick=async()=>{
  const d=window.CPE_TAKE_DEMOS.find(x=>x.id===el('example').value);if(!d)return;
  try{
   if(!await loadManifest(d.manifest))return;
   demo=true;
   const blobs=d.assets.map(s=>new Blob([Uint8Array.from(atob(s),c=>c.charCodeAt(0))],{type:'video/mp4'}));
   await loadMedia(blobs,generation);
  }catch(err){reset();notify(err.message);}
 };
 el('play').onclick=play;el('pause').onclick=()=>{stop();remember();};el('sound').onchange=()=>{sound();remember();};
 el('seek').oninput=e=>{stop();seek(Number(e.target.value));remember();};
 el('go-time').onclick=()=>{
  const text=el('time-entry').value.trim().replace(/\s*s$/i,'').replace(',','.');
  const ms=Math.round(Number(text)*1000);
  if(!/^\d+(\.\d{1,3})?$/.test(text)||!Number.isSafeInteger(ms)||ms>commonEnd){notify('Informe um instante dentro do par em segundos, por exemplo 4,200.');return;}
  stop();seek(ms);remember();
 };
 el('time-entry').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();el('go-time').onclick();}};
 el('swap').onclick=()=>{const s=el('screens');s.insertBefore(s.lastElementChild,s.firstElementChild);remember();};
 el('loop').onclick=toggleLoop;
 for(const id of ['mark','start','end'])el(id).onclick=()=>marker(id);
 for(const id of ['choice','reason','scope','authorize'])el(id).oninput=()=>{clearMessage();remember();};
 el('prepare').onclick=()=>{clearMessage();try{const vote=makeVote();
  if(vote.preference_scope==='scene'&&!manifest.shot?.scene_beat)throw Error('Apresente um par ligado à cena para usar este escopo.');
  el('out').value=activeDeskPair?conversationVote(vote):(demo?'Ensaio local. ':'')+'Solicito registrar esta preferência após conferir o par na planilha.\nCPE_TAKE_VOTE\n'+JSON.stringify(vote,null,2);el('out').hidden=false;el('copy').disabled=false;notify('Decisão preparada. Diga sua escolha na conversa ou copie a mensagem.');}catch(err){notify(err.message);}};
 el('copy').onclick=async()=>{try{await navigator.clipboard.writeText(el('out').value);notify('Copiado. Envie como nova mensagem ao agente.');}catch{el('out').focus();el('out').select();notify('Texto selecionado. Copie e envie ao agente.');}};
 window.addEventListener('pagehide',reset);
 window.addEventListener('keydown',e=>{
  if(e.altKey||e.ctrlKey||e.metaKey||e.repeat||/^(INPUT|TEXTAREA|SELECT|BUTTON|A|SUMMARY)$/.test(e.target?.tagName)||e.target?.isContentEditable||players.size!==2)return;
  const key=e.key.toLowerCase();
  if(key===' '){e.preventDefault();if(isPlaying)stop();else void play();}
  else if(key==='r'){e.preventDefault();void toggleLoop();}
  else if(['i','m','o'].includes(key)){e.preventDefault();marker({i:'start',m:'mark',o:'end'}[key]);}
 });
 window.CPE_MEDIA_CHUNKS=(id,parts)=>sidecarLoads.get(id)?.accept(parts);
 void setupDesk();
}
setup();
