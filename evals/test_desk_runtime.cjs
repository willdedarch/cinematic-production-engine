/* Production desk controller, exercised without a browser, external connection or real vote. */
'use strict';
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), assert=require('node:assert/strict');
const dir=path.join(__dirname,'../panels');
class Element{
  constructor(name){this.name=name;this.children=[];this.textContent='';this.attrs={};this.value='';}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  setAttribute(k,v){this.attrs[k]=v;}
  getAttribute(k){return this.attrs[k];}
  removeAttribute(k){delete this.attrs[k];}
  querySelector(selector){return selector==='h1'?find(this,n=>n.name==='h1'):null;}
  focus(){this.focused=true;}
}
function find(el,predicate){
  if(predicate(el))return el;
  for(const child of el.children){const x=find(child,predicate);if(x)return x;}
}
function text(el){return [el.textContent,...el.children.map(text)].filter(Boolean).join(' ');}
function exactText(el){return el.textContent+el.children.map(exactText).join('');}
function elements(el,pred){return [...(pred(el)?[el]:[]),...el.children.flatMap(child=>elements(child,pred))];}
const surface=fs.readFileSync(path.join(dir,'desk.js'),'utf8');
const storage=new Map();
const state={
  version:1,spreadsheet_id:'DEMO',series:{id:'PROJECT',name:'Série de teste',is_test:true},episode:{id:'EP2',number:2,title:'A chegada'},
  read_at:'2026-11-24T12:31:00Z',workflow:[],
  shots:[{id:'SH05',label:'Oferta',duration_s:6,scene:'Estação',revision:1,states:{out:{cantil:'Lia.esquerda'}},links:[]},
         {id:'SH06',label:'Resposta',duration_s:10,scene:'Estação',revision:2,action:'Lia bebe.',sound:'Buzina',states:{in:{cantil:'Lia.esquerda'}},links:[],
          temporal:{previous_sequence:0,precision:'beat',positions:[{sequence:5,beat:'SH06'}]}}],
  pairs:[{shot_id:'SH06',manifest:{pair_id:'TEST-PAIR'},media:{}}],queue:[{id:'P1',title:'Escolher pausa',shot_id:'SH06',status:'PROPOSTA'}],
  alternatives:[{id:'A1',title:'Som antes do olhar',shot_id:'SH06',status:'PROPOSTA'}],
  bible:{timeline:[{kind:'character_knowledge',subject:'DAVI',key:'chegada',value:'desconhecida',episode_number:1,sequence:63,beat:'SH06',source:{id:'D-EP1',revision:1}},
                   {kind:'character_knowledge',subject:'DAVI',key:'chegada',value:'a vizinha apareceu',episode_number:2,sequence:5,beat:'SH06',source:{id:'D-EP2',revision:1},previous_decision_id:'D-EP1'},
                   {kind:'audience_knowledge',subject:'AUDIENCE',key:'água',value:'escassa',episode_number:1,sequence:2,beat:'SH01',source:{id:'A0',revision:1}}],
         proposals:[{kind:'character_knowledge',subject:'DAVI',key:'chegada',value:'hipótese futura',episode_number:2,sequence:9,beat:'SH09'}]},
  materials:{Screenplays:[{id:'ROTEIRO',title:'Texto local',revision:3,text_or_ref:'DAVI entra pela porta.'}]}
};
function open(data,hash='#inicio',device=storage){
  const ids=Object.fromEntries(['desk','advanced','sheetLink'].map(k=>[k,new Element(k)]));ids.sheetLink.href='https://docs.google.com/spreadsheets/d/test/edit';
  const location={hash};const events={};
  const ctx=vm.createContext({window:{CPE_DESK_DATA:data,addEventListener:(evt,fn)=>events[evt]=fn},
    document:{getElementById:k=>ids[k],createElement:k=>new Element(k),querySelectorAll:()=>[]},location,
    localStorage:{getItem:k=>device.get(k),setItem:(k,v)=>device.set(k,v)},URLSearchParams,requestAnimationFrame:fn=>fn()});
  vm.runInContext(surface,ctx);
  return {host:ids.desk,ids,go(url){location.hash=url;events.hashchange();}};
}
let count=0;
function check(fn){fn();count++;}
let app=open(state);
check(()=>{assert.match(text(app.host),/A chegada/);assert.match(text(app.host),/Escolher pausa/);assert.equal(find(app.host,x=>x.textContent==='Continuar episódio').href,'#plano=SH06');});
check(()=>{assert.ok(find(app.host,n=>n.textContent==='Revisar SH06 · Resposta'));app.go('#plano=SH06');assert.match(text(app.host),/Saída de SH05 · Oferta/);assert.match(text(app.host),/Entrada de SH06 · Resposta/);assert.match(text(app.host),/Som antes do olhar/);});
check(()=>{const a=find(app.host,n=>n.textContent==='Comparar takes');assert.equal(a.href,'takes.html?pair=TEST-PAIR&shot=SH06');});
check(()=>{assert.match(text(app.host),/desconhecida/);assert.match(text(app.host),/Público/);assert.doesNotMatch(text(app.host),/a vizinha apareceu|hipótese futura/);});
check(()=>{const pick=find(app.host,x=>x.name==='select');pick.value='5';pick.onchange();assert.match(text(app.host),/a vizinha apareceu/);assert.match(text(app.host),/Antes · desconhecida/);assert.doesNotMatch(text(app.host),/hipótese futura/);});
check(()=>{const field=label=>find(app.host,n=>n.attrs['aria-label']===label);field('Personagem').value='Davi';field('Assunto').value='chegada';field('Informação pressuposta').value='outra pessoa';find(app.host,n=>n.textContent==='Conferir informação').onclick();assert.match(text(app.host),/Diverge do fato registrado/);assert.match(text(app.host),/Decisão D-EP2/);});
check(()=>{const t=find(app.host,n=>n.name==='textarea');t.value='Preservar a pausa';t.oninput();assert.match(text(app.host),/salvo neste dispositivo/);app.go('#fila');app.go('#plano=SH06');assert.equal(find(app.host,n=>n.name==='textarea').value,'Preservar a pausa');});
check(()=>{app=open(state);assert.match(text(app.host),/Último plano trabalhado/);app.go('#plano=SH06');assert.equal(find(app.host,n=>n.name==='textarea').value,'Preservar a pausa');assert.equal(find(app.host,n=>n.name==='select').value,'5');});
check(()=>{const changed=structuredClone(state);changed.shots[1].revision++;const scoped=open(changed,'#plano=SH06');assert.match(text(scoped.host),/versão do material mudou/);assert.equal(find(scoped.host,n=>n.name==='textarea').value,'Preservar a pausa');});
check(()=>{const changed=structuredClone(state);changed.episode.id='EP3';const scoped=open(changed,'#plano=SH06');assert.equal(find(scoped.host,n=>n.name==='textarea').value,'');});
check(()=>{app.go('#roteiro');assert.match(text(app.host),/DAVI entra pela porta/);app.go('#takes');assert.equal(find(app.host,n=>n.textContent==='Abrir este par').href,'takes.html?pair=TEST-PAIR&shot=SH06');});
check(()=>{const absent=open(null);for(const route of ['#roteiro','#takes','#planos','#fila','#oficina','#plano=SH06','#inicio'])absent.go(route);assert.match(text(absent.host),/abre meu episódio/);});
check(()=>{const lost={get(){throw Error('indisponível');},set(){throw Error('indisponível');}};const limited=open(state,'#plano=SH06',lost);const t=find(limited.host,n=>n.name==='textarea');t.value='Nota ainda visível';t.oninput();assert.match(text(limited.host),/Não foi possível salvar/);limited.go('#fila');limited.go('#plano=SH06');assert.equal(find(limited.host,n=>n.name==='textarea').value,'Nota ainda visível');});
check(()=>{const corrupted=structuredClone(state);corrupted.shots[0].thumbnail='javascript:alert(1)';corrupted.queue_url='javascript:alert(1)';const a=open(corrupted,'#planos');assert.ok(elements(a.host,n=>n.name==='img').every(n=>!String(n.src).startsWith('javascript:')));a.go('#fila');assert.equal(find(a.host,n=>n.textContent==='Abrir fila no Sheets').href,a.ids.sheetLink.href);});
check(()=>{const changed=structuredClone(state);changed.shots[1].presentation='Frame original ausente';changed.shots[1].continuity_review=[{field:'cantil',before:'Lia',after:'Davi',status:'JUSTIFIED',decisions:[{id:'Exceção de direção',revision:2,reason:'Passagem vista no reflexo'}]}];const a=open(changed,'#plano=SH06');assert.match(text(a.host),/Passagem vista no reflexo/);assert.match(text(a.host),/Exceção justificada/);assert.match(text(a.host),/Frame original ausente/);assert.doesNotMatch(text(a.host),/a divergência ainda precisa/i);});
check(()=>{const changed=structuredClone(state);changed.shots[0].scene='Chegada';const a=open(changed,'#planos'),sel=find(a.host,n=>n.name==='select');sel.value='Chegada';sel.onchange();const list=find(a.host,n=>n.className==='plan-list');assert.match(text(list),/Oferta/);assert.doesNotMatch(text(list),/Resposta/);});
check(()=>{const changed=structuredClone(state);changed.queue=[];changed.shots[1].preferences=[{choice:'B',mark_ms:4200,start_ms:3800,end_ms:4600,reason:'A pausa preserva a dúvida',scope:'scene',confirmed:true,current:false,shot_revision:1,pair_id:'TEST-PAIR',takes:{A:{id:'A-v1',version:1,revision:2},B:{id:'B-v2',version:2,revision:3}},source:{id:'HF-2',revision:1}}];const a=open(changed);assert.doesNotMatch(text(a.host),/Ouvir o par/);a.go('#plano=SH06');assert.match(text(a.host),/Take B · 4,2 s/);assert.match(text(a.host),/A pausa preserva a dúvida/);assert.match(text(a.host),/Decisão confirmada por releitura/);assert.match(text(a.host),/Take escolhido Em aberto/);assert.match(text(a.host),/versão apresentada anteriormente/);});
const css=fs.readFileSync(path.join(dir,'desk.css'),'utf8');
check(()=>{assert.match(css,/:focus-visible/);assert.match(css,/@media\(max-width:700px\)/);assert.match(css,/overflow-x:auto/);});
check(()=>{app.go('#fila');const h=find(app.host,n=>n.name==='h1');assert.equal(h.tabIndex,-1);assert.equal(h.focused,true);});
const lines='ESTAÇÃO · DIA\r\nDavi olha a porta.\r\nDAVi: Quem chegou?\r\n\r\n   DAVI (V.O.) ^\r\nUm instante.\r\n\r\n@Lia\r\nJá volto.\r\nDIREÇÃO: aguarde.\r\n';
const screenplayState=structuredClone(state);
screenplayState.materials.Screenplays[0].text_or_ref=lines;
screenplayState.materials.Characters=[{name:'Lia'}];
const reader=open(screenplayState,'#roteiro');
const pre=find(reader.host,n=>n.className==='screenplay'), sheet=find(reader.host,n=>n.className==='speaker-sheet');
const cues=elements(pre,n=>n.className==='character-cue');
check(()=>{assert.equal(exactText(pre),lines);assert.deepEqual(cues.map(c=>c.textContent),['DAVi','DAVI','Lia']);assert.ok(cues.every(c=>c.name==='button' && c.attrs['aria-controls']===sheet.id));assert.ok(sheet.hidden);});
check(()=>{cues[0].onclick();assert.equal(cues[0].attrs['aria-expanded'],'true');assert.ok(find(sheet,n=>n.name==='h2').focused);assert.equal(find(sheet,n=>n.name==='blockquote').textContent,'Quem chegou?');assert.match(text(sheet),/abertura do episódio/);assert.match(text(sheet),/desconhecida/);assert.match(text(sheet),/escassa/);assert.doesNotMatch(text(sheet),/a vizinha apareceu|D-EP2|hipótese futura/);});
check(()=>{const place=find(sheet,n=>n.attrs['aria-label']==='Plano ou cena de referência');place.value='SH06';place.onchange();const moment=find(sheet,n=>n.className==='speaker-facts');const pick=find(moment,n=>n.name==='select');assert.equal(pick.value,'0');pick.value='5';pick.onchange();assert.match(text(moment),/a vizinha apareceu/);assert.match(text(moment),/Decisão D-EP2/);assert.doesNotMatch(text(moment),/hipótese futura/);});
check(()=>{find(sheet,n=>n.textContent==='Voltar à fala').onclick();assert.ok(sheet.hidden);assert.ok(cues[0].focused);assert.equal(cues[0].attrs['aria-expanded'],'false');cues[1].onclick();assert.doesNotMatch(text(sheet),/a vizinha apareceu/);assert.match(text(sheet),/desconhecida/);assert.equal(exactText(pre),lines);});
check(()=>{cues[2].onclick();assert.equal(cues[1].attrs['aria-expanded'],'false');assert.match(text(sheet),/Conhecimento de Lia desconhecido/);assert.match(text(sheet),/escassa/);assert.doesNotMatch(text(sheet),/D-EP1|D-EP2/);});
if(process.argv.includes('--projection')){
  const projected=JSON.parse(fs.readFileSync(0,'utf8').replace(/^\uFEFF/,''));
  check(()=>{assert.equal(projected.version,1);const a=open(projected);assert.ok(text(a.host).includes(projected.episode.title));a.go('#fila');a.go('#roteiro');a.go('#planos');
    for(const shot of projected.shots){
      a.go('#plano='+encodeURIComponent(shot.id));
      assert.ok(text(a.host).includes(shot.action));assert.ok(text(a.host).includes('Bíblia na cena'));
      assert.ok(find(a.host,n=>n.name==='textarea'));const m=find(a.host,n=>n.name==='select');assert.ok(m.children.length);
      for(const p of shot.preferences||[]){
        assert.ok(text(a.host).includes(p.reason));if(p.confirmed)assert.match(text(a.host),/Decisão confirmada por releitura/);
        assert.ok(text(a.host).includes(p.source.id));
      }
    }
  });
  if(process.argv.includes('--rehearsal-dialogue'))check(()=>{
    assert.equal(projected.series.id,'TEST-CPE13');
    const a=open(projected,'#roteiro'),doc=find(a.host,n=>n.className==='screenplay' && exactText(n).includes('DAVI: Quem chegou?'));
    const d=find(a.host,n=>n.id===find(doc,n=>n.textContent==='DAVI').attrs['aria-controls']);
    find(doc,n=>n.textContent==='DAVI').onclick();
    assert.match(text(d),/identidade desconhecida/);assert.match(text(d),/Rosa está na estação/);assert.doesNotMatch(text(d),/é Rosa/);
    const sh=projected.shots.find(s=>s.label==='SH06');assert.ok(sh);
    const cut=find(d,n=>n.attrs['aria-label']==='Plano ou cena de referência');cut.value=sh.id;cut.onchange();
    assert.doesNotMatch(text(d),/é Rosa/);
    const moment=find(find(d,n=>n.className==='speaker-facts'),n=>n.name==='select');
    assert.ok(moment.children.some(el=>el.value==='68'));moment.value='68';moment.onchange();assert.match(text(d),/é Rosa/);
    const decision=projected.bible.timeline.find(f=>f.subject==='DAVI' && f.sequence===68).source.id;
    assert.ok(text(d).includes(decision));
    a.go('#plano='+encodeURIComponent(sh.id));assert.match(text(a.host),/Saída de SH05/);assert.match(text(a.host),/Entrada de SH06/);
  });
}
console.log(JSON.stringify({tests:count,passed:count,environment:'production desk JS; DOM and storage doubles',browser_verified:false,network_calls:0}));
