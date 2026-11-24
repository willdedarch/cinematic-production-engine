/* Actual panel JS executed against a minimal DOM test double. This is NOT browser QA. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
class Element{
 constructor(tag){this.tagName=tag;this.children=[];this.value='';this.checked=false;this.disabled=false;this.hidden=false;this.dataset={};this.textContent='';}
 append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=[...nodes];}focus(){}select(){}click(){return this.onclick?.();}
}
const ids=['message','scope','freshness','progressText','progress','nav','panel','authorize','outgoing','copy','import','file','export','boardSelect','boardPanel','decisionSummary'];const nodes=Object.fromEntries(ids.map(x=>[x,new Element(x)]));
const document={getElementById:id=>nodes[id],createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})};
const ctx=vm.createContext({window:{},document,crypto:webcrypto,TextEncoder,Blob,URL,setTimeout,console,navigator:{clipboard:{writeText:async()=>{}}}});
for(const file of ['catalog.js','boards.js','studio.js','boards-runtime.js'])vm.runInContext(fs.readFileSync(path.join(root,'panels',file),'utf8'),ctx);
const run=s=>vm.runInContext(s,ctx);let tests=0;const pass=()=>tests++;
(async()=>{
 assert.equal(nodes.nav.children.length,16);assert.match(nodes.scope.textContent,/Nenhum/);pass();
 await run("prepare('INIT')");assert.match(nodes.message.textContent,/Marque a autorização/);assert.equal(nodes.outgoing.value,'');pass();
 nodes.authorize.checked=true;run("getDraft().values.project_name='Teste local'");await run("prepare('INIT')");let p=JSON.parse(nodes.outgoing.value.split('CPE_INTENT\n')[1]);assert.equal(p.action,'INIT');assert.equal(p.scope,null);pass();
 const fixture=JSON.parse(fs.readFileSync(path.join(root,'templates/shared-state.test-fixture.json'),'utf8'));
 await nodes.file.onchange({target:{files:[{size:1000,text:async()=>JSON.stringify(fixture)}],value:'fixture'}});assert.equal(nodes.authorize.checked,false);assert.equal(nodes.outgoing.value,'');pass();
 const baseline=run('JSON.stringify(snapshot)');
 for(let i=0;i<16;i++){nodes.nav.children[i].click();assert.match(nodes.panel.children[0].textContent,new RegExp('G'+i+' ·'));assert.equal(run('Object.keys(getDraft().checks).length'),fixture.tables.Checklists.filter(c=>c.gate_id==='G'+i).length);}pass();
 nodes.nav.children[0].click();nodes.authorize.checked=true;run("getDraft().values.genre='drama'; getDraft().checks['TEST-CK-G0-1'].checked=true; getDraft().checks['TEST-CK-G0-1'].evidence='manual local'");await run("prepare('SAVE_CHOICES')");p=JSON.parse(nodes.outgoing.value.split('CPE_INTENT\n')[1]);assert.equal(p.action,'SAVE_CHOICES');assert.equal(p.expected_revision,1);assert.match(p.base_scope_sha256,/^[a-f0-9]{64}$/);assert.equal(p.base_guards,undefined);assert.equal(run('JSON.stringify(snapshot)'),baseline);pass();
 await run("prepare('APPROVE')");assert.equal(nodes.outgoing.value,'');assert.equal(nodes.copy.disabled,true);assert.match(nodes.message.textContent,/Cada critério/);pass();
 await run("prepare('REVISE')");assert.match(nodes.message.textContent,/motivo/);pass();
 run("getDraft().reason='corrigir apenas porta';");await run("prepare('REVISE')");p=JSON.parse(nodes.outgoing.value.split('CPE_INTENT\n')[1]);assert.equal(p.reason,'corrigir apenas porta');assert.equal(run('JSON.stringify(snapshot)'),baseline);pass();
 let bad=structuredClone(fixture);bad.tables.Workflow.pop();await nodes.file.onchange({target:{files:[{size:100,text:async()=>JSON.stringify(bad)}],value:''}});assert.match(nodes.message.textContent,/16 gates/);assert.equal(run('JSON.stringify(snapshot)'),baseline);pass();
 const malicious=structuredClone(fixture);malicious.tables.Decisions[0].topic='<script>send()</script>';assert.doesNotThrow(()=>run('validateSnapshot('+JSON.stringify(malicious)+')'));assert.equal(typeof ctx.send,'undefined');pass();
 for(const b of ctx.window.CPE_BOARDS){run('showBoard('+JSON.stringify(b.id)+')');assert.equal(nodes.boardPanel.children[0].textContent,b.title);assert.equal(nodes.panel.hidden,true);}pass();
 nodes.authorize.checked=false;run("showBoard('references')");await run("prepareBoard('references','SELECT')");assert.equal(nodes.outgoing.value,'');pass();
 nodes.authorize.checked=true;run("supportDrafts.references.observation='Diagrama autoral; geometria observável';supportDrafts.references.target='REF-TECH-BLOCKING rev1'");await run("prepareBoard('references','APPROVE')");assert.match(nodes.message.textContent,/critérios/);pass();
 run("supportDrafts.references.checks={0:true,1:true,2:true}");await run("prepareBoard('references','APPROVE')");p=JSON.parse(nodes.outgoing.value.split('CPE_INTENT\n')[1]);assert.equal(p.action,'BOARD_APPROVE');assert.equal(p.board_id,'references');assert.equal(run('JSON.stringify(snapshot)'),baseline);pass();
 nodes.nav.children[0].click();assert.equal(nodes.boardPanel.hidden,true);assert.equal(nodes.panel.hidden,false);pass();
 await nodes.file.onchange({target:{files:[{size:1000,text:async()=>JSON.stringify(fixture)}],value:'new-scope'}});assert.equal(run('Object.keys(supportDrafts).length'),0);assert.equal(nodes.authorize.checked,false);assert.equal(nodes.outgoing.value,'');pass();
 run("showBoard('blind-comparison');supportDrafts['blind-comparison'].observation='O timing é decisivo';");
 nodes.authorize.checked=true;await run("prepareBoard('blind-comparison','COMPARE')");assert.equal(nodes.outgoing.value,'');assert.match(nodes.message.textContent,/Identifique o par/);pass();
 run("supportDrafts['blind-comparison'].values.packet='PAR-TESTE@1';supportDrafts['blind-comparison'].values.choice='B';");
 await run("prepareBoard('blind-comparison','COMPARE')");assert.match(nodes.outgoing.value,/"choice": "B"/);pass();
 const serialized=JSON.parse(run('JSON.stringify(draftFile())'));
 async function upload(obj){await nodes.file.onchange({target:{files:[{size:1000,text:async()=>JSON.stringify(obj)}],value:'test'}});}
 await upload(fixture);await upload(serialized);
 assert.equal(run('board'),'blind-comparison');assert.equal(run("supportDrafts['blind-comparison'].observation"),'O timing é decisivo');assert.equal(run('restoredNeedsFresh'),true);assert.equal(nodes.authorize.checked,false);pass();
 nodes.authorize.checked=true;await run("prepareBoard('blind-comparison','COMPARE')");assert.match(nodes.message.textContent,/leitura atual/);pass();
 const revised=structuredClone(fixture);revised.tables.Projects[0].name='Outra revisão real';await upload(revised);
 assert.match(nodes.message.textContent,/Conflito de versões/);assert.equal(run('restoredNeedsFresh'),true);assert.equal(run("supportDrafts['blind-comparison'].values.choice"),'B');pass();
 assert.deepEqual(Array.from(run("pendingReconcile.changes[0].fields")),['name']);run("resolveDraftConflict('notes')");
 assert.equal(run('restoredNeedsFresh'),false);assert.equal(run("supportDrafts['blind-comparison'].values.choice"),undefined);assert.equal(run("supportDrafts['blind-comparison'].observation"),'O timing é decisivo');assert.equal(nodes.authorize.checked,false);pass();
 await upload(serialized);
 await upload(fixture);assert.equal(run('restoredNeedsFresh'),false);assert.equal(nodes.authorize.checked,false);assert.equal(run('board'),'blind-comparison');pass();
 await upload({kind:'LOCAL_DRAFT_NOT_SAVED',selected:'G0',drafts:serialized.drafts,snapshot:fixture});
 assert.equal(run('board'),'phase');assert.equal(run('restoredNeedsFresh'),true);pass();
 await upload(fixture);nodes.authorize.checked=true;await run("prepare('SAVE_CHOICES')");assert.equal(nodes.copy.disabled,false);assert.match(nodes.decisionSummary.textContent,/Registrar escolhas/);assert.equal(nodes.decisionSummary.hidden,false);
 nodes.nav.children[2].click();assert.equal(nodes.copy.disabled,true);assert.equal(nodes.authorize.checked,false);assert.equal(nodes.decisionSummary.hidden,true);pass();
 nodes.authorize.checked=true;await run("prepare('SAVE_CHOICES')");nodes.authorize.checked=false;nodes.authorize.onchange();
 assert.equal(nodes.outgoing.value,'');assert.equal(nodes.copy.disabled,true);pass();
 run("getDraft().reason='Guardar a minha nota';registerEdit()");await upload(fixture);
 assert.equal(run('getDraft().reason'),'Guardar a minha nota');assert.equal(run('selected'),'G2');pass();
 assert.notDeepEqual(Array.from(run("boardActions('cast-compare').map(a=>a[1])")),Array.from(run("boardActions('visual-lab').map(a=>a[1])")));pass();
 const result={tests,passed:tests,support_boards:ctx.window.CPE_BOARDS.length,environment:'Node VM with minimal DOM test double',browser_verified:false,network_calls:0};console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1;});
