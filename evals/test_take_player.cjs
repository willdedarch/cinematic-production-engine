/* Exercise the shipped controller. The fake media clock and DOM do not verify browser decoding. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
class Element {
 constructor(tag){
  this.tag=tag;this.children=[];this.listeners={};this.value='';this.textContent='';this.checked=false;
  if(tag==='audio'||tag==='video'){this.currentTime=0;this.duration=6;this.muted=false;this.paused=true;this.ended=false;}
 }
 addEventListener(key,cb){this.listeners[key]=cb;}
 set src(value){queueMicrotask(()=>this.listeners[this.tag==='img'?'load':'loadedmetadata']?.());}
 pause(){this.paused=true;}
 async play(){this.paused=false;}
 setAttribute(k,v){this[k]=v;}
 append(...v){this.children.push(...v);}
 replaceChildren(...v){this.children=v;}
 get lastElementChild(){return this.children[this.children.length-1];}get firstElementChild(){return this.children[0];}
 insertBefore(item,before){this.children=this.children.filter(v=>item!==v);this.children.splice(this.children.indexOf(before),0,item);}
}
const html=fs.readFileSync(path.join(root,'panels/takes.html'),'utf8');
const nodes=Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new Element(m[1])]));
nodes.scope.value='deliverable';nodes.sound.value='A';nodes.screens.children=[nodes.left,nodes.right];
const ctx=vm.createContext({window:{addEventListener(){}},document:{getElementById:key=>nodes[key],createElement:v=>new Element(v)},
  Blob,URL,URLSearchParams,TextEncoder,Uint8Array,atob,crypto:webcrypto,requestAnimationFrame:()=>1,cancelAnimationFrame:()=>{},
  clearTimeout,setTimeout,navigator:{clipboard:{writeText:async()=>{}}}});
for(const f of ['take-demos.js','take-player.js'])vm.runInContext(fs.readFileSync(path.join(root,'panels',f),'utf8'),ctx);
const run=s=>vm.runInContext(s,ctx);
async function main(){
 let count=0;
 for(const caseId of ['COM-01','DOC-01','SUS-01']){
  nodes.example.value=caseId;await nodes['load-demo'].onclick();
  assert.equal(run('players.size'),2);assert.equal(nodes.seek.max,'6000');assert.equal(nodes.choice.value,'');count++;
 }
 nodes.prepare.onclick();assert.match(nodes.status.textContent,/autorização/);count++;
 nodes.authorize.checked=true;nodes.prepare.onclick();assert.match(nodes.status.textContent,/explicitamente/);count++;
 nodes.choice.value='B';nodes.reason.value='Prefiro a pausa antes do gesto.';nodes.prepare.onclick();assert.match(nodes.status.textContent,/Marque um instante/);count++;
 nodes.seek.oninput({target:{value:'4200'}});nodes.mark.onclick();assert.equal(run("players.get('B').currentTime"),4.2);
 nodes.sound.value='B';nodes.sound.onchange();assert.equal(run("players.get('A').muted"),true);assert.equal(run("players.get('B').muted"),false);count++;
 await nodes.play.onclick();run("players.get('B').currentTime=4.7; players.get('A').currentTime=4.4; tick()");
 assert.equal(run("players.get('A').currentTime"),4.7);nodes.pause.onclick();assert.equal(run("players.get('A').paused"),true);count++;
 nodes.seek.oninput({target:{value:'3900'}});nodes.start.onclick();nodes.seek.oninput({target:{value:'4500'}});nodes.end.onclick();
 nodes.swap.onclick();assert.strictEqual(nodes.screens.children[0],nodes.right);
 nodes.prepare.onclick();const vote=JSON.parse(nodes.out.value.split('CPE_TAKE_VOTE\n')[1]);
 assert.deepEqual([vote.start_ms,vote.mark_ms,vote.end_ms],[3900,4200,4500]);assert.equal(vote.choice,'B');
 assert.equal(vote.pair_sha256,ctx.window.CPE_TAKE_DEMOS[2].manifest.pair_sha256);assert.equal(vote.demonstration,true);count++;
 const blob=new Blob(['different bytes']);await nodes.clips.onchange({target:{files:[blob,blob]}});
 assert.equal(run('players.size'),0);assert.equal(nodes.authorize.checked,false);assert.match(nodes.status.textContent,/não correspondem/);count++;
 const d=ctx.window.CPE_TAKE_DEMOS[0],m=JSON.parse(JSON.stringify(d.manifest));
 m.shot={id:'SH06',revision:1,scene_beat:'Estação',sha256:'e'.repeat(64)};
 ctx.rev=m;delete m.pair_sha256;
 m.pair_sha256=await run('sha(new TextEncoder().encode(JSON.stringify(canonical(rev))))');
 const item={shot_id:'SH06',manifest:m,media:{}};
 const byHash=new Map(d.assets.map(b64=>[require('crypto').createHash('sha256').update(Buffer.from(b64,'base64')).digest('hex'),b64]));
 for(const label of ['A','B'])item.media[label]='data:video/mp4;base64,'+byHash.get(m.takes[label].sha256);
 ctx.window.CPE_DESK_DATA={series:{id:m.project_id},episode:{id:m.episode_id,title:'O cantil'},pairs:[item]};
 ctx.window.location={search:'?pair='+m.pair_id+'&shot=SH06'};
 const saved=new Map();ctx.window.localStorage={getItem:k=>saved.get(k),setItem:(k,v)=>saved.set(k,v)};
 await run('setupDesk()');assert.equal(nodes.return.href,'studio.html#plano=SH06');assert.equal(run('players.size'),2);count++;
 for(const [id,ms] of [['start',3800],['mark',4200],['end',4600]]){nodes.seek.oninput({target:{value:String(ms)}});nodes[id].onclick();}
 nodes.sound.value='A';nodes.sound.onchange();await nodes.loop.onclick();assert.equal(nodes.loop['aria-pressed'],'true');
 for(let i=0;i<3;i++){
  run("players.get('A').currentTime=4.61;players.get('B').currentTime=4.61;tick()");
  assert.equal(run("players.get('A').currentTime"),3.8);assert.equal(run("players.get('B').currentTime"),3.8);
  nodes.sound.value=i===1?'A':'B';nodes.sound.onchange();nodes.swap.onclick();
 }
 assert.equal(run('isPlaying'),true);assert.equal(run('segment.mark_ms'),4200);count++;
 nodes.pause.onclick();assert.equal(run('isPlaying'),false);assert.equal(run('looping'),true);
 nodes['time-entry'].value='4,350';nodes['go-time'].onclick();assert.equal(run('current'),4350);count++;
 nodes['time-entry'].value='9';nodes['go-time'].onclick();assert.equal(run('current'),4350);count++;
 nodes.choice.value='B';nodes.scope.value='scene';nodes.reason.value='A respiração segura o corte.';nodes.reason.oninput();
 nodes.authorize.checked=true;nodes.prepare.onclick();
 assert.match(nodes.out.value,/SH06/);assert.match(nodes.out.value,/4,200 s/);assert.doesNotMatch(nodes.out.value,/CPE_TAKE_VOTE/);count++;
 assert.ok(nodes.out.value.includes('Par apresentado: '+m.pair_id));
 assert.ok(nodes.out.value.includes('Versão do par: '+m.pair_sha256));count++;
 await run('setupDesk()');assert.equal(nodes.reason.value,'A respiração segura o corte.');assert.equal(nodes.scope.value,'scene');
 assert.equal(nodes.authorize.checked,false);assert.equal(nodes.copy.disabled,true);assert.equal(run('segment.mark_ms'),4200);count++;
 nodes.seek.oninput({target:{value:'5000'}});nodes.mark.onclick();assert.equal(run('segment.end_ms'),4600);assert.equal(run('segment.mark_ms'),5000);
 nodes.authorize.checked=true;nodes.prepare.onclick();assert.match(nodes.status.textContent,/dentro do trecho/);count++;
 item.media.A='data:video/mp4;base64,'+Buffer.from('outra versão').toString('base64');
 await run('setupDesk()');assert.equal(run('players.size'),0);assert.match(nodes.status.textContent,/não correspondem/);count++;
 item.media.A='data:video/mp4;base64,'+byHash.get(m.takes.A.sha256);
 ctx.window.location={search:''};
 await run('setupDesk()');
 assert.equal(run('players.size'),2);assert.equal(nodes.return.href,'studio.html#plano=SH06');count++;
 item.manifest={...m,pair_sha256:'a'.repeat(64)};
 await run('setupDesk()');
 assert.equal(run('players.size'),0);assert.equal(nodes.play.disabled,true);
 assert.match(nodes.status.textContent,/O manifesto foi alterado/);count++;
 item.manifest=m;
 ctx.crypto=undefined;
 await run('setupDesk()');
 assert.equal(run('players.size'),0);assert.equal(nodes.play.disabled,true);
 assert.match(nodes.status.textContent,/não disponibiliza a verificação de integridade/);count++;
 ctx.crypto=webcrypto;
 const previews=d.assets.map(s=>new Blob([Buffer.from(s,'base64')],{type:'video/mp4'}));
 await nodes['preview-files'].onchange({target:{files:previews}});
 assert.equal(run('players.size'),2);assert.equal(run('manifest.kind'),'LOCAL_EXPLORATION');
 await nodes.play.onclick();assert.equal(run('isPlaying'),true);nodes.pause.onclick();nodes.prepare.onclick();
 assert.equal(nodes.copy.disabled,true);assert.match(nodes.status.textContent,/vincular os dois arquivos/);count++;
 await nodes['preview-files'].onchange({target:{files:[previews[0],previews[0]]}});
 assert.equal(run('players.size'),0);assert.match(nodes.status.textContent,/idênticos/);count++;
 console.log(JSON.stringify({tests:count,passed:count,environment:'real controller; DOM and media clock doubles',browser_media_verified:false}));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
