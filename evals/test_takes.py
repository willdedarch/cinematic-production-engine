import array, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shared_state import StateError, validate
from takes import take_pair, vote_plan, media_hash
from judgment import native_metrics, take_preferences, consolidate, blind_packets, review_packet, digest

def load(name):return json.loads((ROOT / name).read_text(encoding='utf-8'))

class TakeReviews(unittest.TestCase):
    def setUp(self):
        self.state = load('examples/takes/demo-state.json')
        self.manifest = load('examples/takes/COM-01-pair.json')
        self.vote = {'kind':'CPE_TAKE_VOTE_1','pair_id':self.manifest['pair_id'],
                     'pair_sha256':self.manifest['pair_sha256'],'choice':'B','start_ms':3900,'mark_ms':4200,
                     'end_ms':4400,'reason':'A pausa dá espaço para perceber a reação.',
                     'preference_scope':'episode','authorized':True,'demonstration':True}
        self.auth = {'actor':'Ensaio automatizado','user_message_ref':'TESTE-NAO-HUMANO','authorized':True}

    def plan(self,**extra):
        return vote_plan(self.state,{'manifest':self.manifest,'vote':self.vote,'authorization':self.auth,**extra})

    def test_all_three_pairs_bind_original_mp4_with_audio(self):
        for case in ('COM-01','DOC-01','SUS-01'):
            pair=load('examples/takes/'+case+'-pair.json')
            self.assertEqual({v['sha256'] for v in pair['takes'].values()},
                             {media_hash(ROOT/'examples/takes'/(case+'-'+str(i)+'.mp4')) for i in (1,2)})
            self.assertTrue(all(v['duration_ms']==6000 and v['mime']=='video/mp4' and v['has_audio'] for v in pair['takes'].values()))

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg optional')
    def test_decode_six_real_clips_and_measure_audible_cues(self):
        for case, approx in [('COM-01',(2.30,2.82)),('DOC-01',(2.65,3.45)),('SUS-01',(2.00,2.00))]:
            for i, expected in enumerate(approx,1):
                media=str(ROOT/'examples/takes'/(case+'-'+str(i)+'.mp4'))
                args=['ffmpeg','-nostdin','-v','error','-i',media]
                pixels=subprocess.check_output(args+['-ss','4.2','-frames:v','1','-an','-pix_fmt','rgb24','-f','rawvideo','-'])
                self.assertEqual(len(pixels),320*180*3)
                self.assertGreater(max(pixels)-min(pixels),50)
                raw=subprocess.check_output(args+['-vn','-ac','1','-ar','8000','-f','s16le','-'])
                samples=array.array('h');samples.frombytes(raw)
                if sys.byteorder=='big':samples.byteswap()
                onset=next(j for j,sample in enumerate(samples) if abs(sample)>700)/8000
                self.assertAlmostEqual(onset,expected,delta=.055)

    @unittest.skipUnless(shutil.which('ffprobe'),'FFprobe optional')
    def test_create_pair_from_registry_and_files(self):
        pair=take_pair(self.state, {**self.manifest,'takes':[{'id':t['id'],'revision':1} for t in self.manifest['takes'].values()],'include_test':True})
        self.assertTrue(all(v['has_audio'] for v in pair['takes'].values()))
        self.assertNotEqual(pair['pair_id'],self.manifest['pair_id'])

    def test_scoped_vote_keeps_both_revisions_and_mark(self):
        candidate=self.plan()['candidate']
        feedback=candidate['tables']['Human Feedback'][-1]
        self.assertEqual(feedback['human_decision'],'PREFER_B')
        evidence=json.loads(feedback['evidence'])
        self.assertEqual((3900,4200,4400),tuple(evidence[k] for k in ('start_ms','mark_ms','end_ms')))
        self.assertEqual(evidence['takes'],self.manifest['takes'])
        self.assertEqual(feedback['user_message_ref'],self.auth['user_message_ref'])
        self.assertTrue(validate(candidate))
        actual=take_preferences(candidate,self.manifest['project_id'],self.manifest['episode_id'],include_test=True)
        self.assertEqual(actual[0]['evidence']['reason'],self.vote['reason'])
        self.assertEqual(actual[0]['origin_status'],'TEST')
        self.assertEqual(take_preferences(candidate,self.manifest['project_id'],'different-ep',include_test=True),[])
        self.assertEqual(native_metrics(candidate,[self.auth['user_message_ref']])['real_human_n'],0)

    def test_preferences_skip_divergent_persisted_evidence(self):
        candidate=self.plan()['candidate']
        pair=candidate['tables']['Pairwise Comparisons'][-1]
        row=candidate['tables']['Human Feedback'][-1]
        def current():
            return take_preferences(candidate,self.manifest['project_id'],self.manifest['episode_id'],include_test=True)
        pair['revision']+=1
        self.assertEqual(current(),[])
        pair['revision']-=1
        row['preference_scope']='project'
        self.assertEqual(current(),[])
        row['preference_scope']='episode'
        row['evidence']=pair['order_results_json']=json.dumps({'kind':'TAKE_PREFERENCE','takes':None})
        self.assertEqual(current(),[])

    def test_old_manifest_and_replaced_file_rejected(self):
        chosen=self.manifest['takes']['B']
        with tempfile.TemporaryDirectory() as directory:
            replaced=Path(directory)/'replacement.mp4';replaced.write_bytes(b'synthetic replacement')
            with self.assertRaisesRegex(StateError,'substituída'):self.plan(paths={chosen['id']:str(replaced)})
        current=next(r for r in self.state['tables']['Artifact Registry'] if r['id']==chosen['id'])
        current['revision']+=1
        with self.assertRaisesRegex(StateError,'versão'):self.plan()

    def test_task_and_judge_reuse_only_authorized_take_scopes(self):
        from episode_workflow import initialize_episode
        from shared_state import prepare
        state=self.state
        pid,ep=self.manifest['project_id'],self.manifest['episode_id']
        state['tables']['Projects'][0]['status']='ACTIVE'
        for scope in ('deliverable','episode','project'):
            state=vote_plan(state,{'manifest':self.manifest,'vote':{**self.vote,'preference_scope':scope},
                                   'authorization':{**self.auth,'user_message_ref':'SYNTHETIC-TEMP-'+scope}})['candidate']
        ep2=pid+'-EP2'
        state=initialize_episode(state,{'project_id':pid,'episode_title':'Outra cena','target_seconds':40,
                                 'new_episode':True,'include_test':True},{**self.auth,'op_id':'SYNTHETIC-EP2'})['candidate']
        artifact=next(r for r in state['tables']['Artifact Registry'] if r['id']==self.manifest['takes']['B']['id'])
        values={k:artifact[k] for k in ('project_id','gate_id','kind','department','version','uri','sha256','origin','rights','status','is_test')}
        state=prepare(state,{**self.auth,'op_id':'SYNTHETIC-EP2-ASSET','at':state['read_at'],
                             'changes':[{'table':'Artifact Registry','id':'SYNTHETIC-OUTRO-TAKE','expected_revision':None,
                                         'values':{**values,'episode_id':ep2}}]})['candidate']
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);snapshot=tmp/'snapshot.json';snapshot.write_text(json.dumps(state),encoding='utf8')
            def cli(command,spec,episode):
                inp=tmp/'spec.json';inp.write_text(json.dumps(spec),encoding='utf8')
                args=[sys.executable,'-B',str(ROOT/'scripts/cpe.py'),command,'--workspace',str(tmp),'--snapshot',str(snapshot),
                      '--input',str(inp),'--project',pid,'--episode',episode,'--include-test','--gate','G10']
                result=subprocess.run(args,capture_output=True,encoding='utf8',cwd=ROOT)
                self.assertEqual(result.returncode,0,result.stderr)
                return json.loads(Path(json.loads(result.stdout)['result']).read_text(encoding='utf8'))
            def scopes(packet):return {p['scope'] for p in packet['take_preferences']}
            first=cli('task',{},ep)
            self.assertEqual(scopes(first),{'episode','project'})
            self.assertNotIn('SYNTHETIC-TEMP-deliverable',json.dumps(first['references_and_lessons']))
            self.assertEqual(scopes(cli('task',{'target_ids':[artifact['id']]},ep)),{'episode','project','deliverable'})
            self.assertEqual(scopes(cli('task',{},ep2)),{'project'})
            spec={'target':{'id':'SYNTHETIC-OUTRO-TAKE','revision':1,'path':str(ROOT/artifact['uri'])},
                  'context':{'genre':'comédia'},'department':'editing'}
            new_judge=cli('judge',spec,ep2)
            self.assertEqual(scopes(new_judge),{'project'})
            item=new_judge['take_preferences'][0]
            self.assertEqual((item['origin_status'],item['evidence']['mark_ms'],item['episode_id']),('TEST',4200,ep))
            self.assertEqual(scopes(cli('judge',{**spec,'holdout':True},ep2)),set())
            spec['target']['id']=artifact['id']
            self.assertEqual(scopes(cli('judge',spec,ep)),{'episode','project','deliverable'})

    def test_explicit_vote_and_valid_clip_required(self):
        for field,value in [('choice',''),('reason','   '),('start_ms',5000),('mark_ms',-1),('end_ms',6001),('pair_sha256','wrong')]:
            with self.subTest(field=field):
                old=self.vote[field];self.vote[field]=value
                with self.assertRaises(StateError):self.plan()
                self.vote[field]=old
        self.auth['authorized']=False
        with self.assertRaises(StateError):self.plan()

    def test_dissent_and_order_effect_are_distinct(self):
        session=blind_packets([{'material_id':'X','text':'escolha um'},{'material_id':'Y','text':'escolha dois'}],{})
        votes=[]
        for i,packet in enumerate(session['public_packets']):
            for critic,order in [('direção',('A','B')),('montagem',('B','A'))]:
                votes.append({'reviewer':critic,'packet_id':packet['packet_id'],'choice':order[i],
                              'rationale':'Tempo do olhar','evidence':['4,2 s']})
        result=consolidate(session,votes)
        self.assertEqual(result['outcome'],'UNRESOLVED')
        self.assertEqual(result['order_changes'],[])
        self.assertEqual(len(result['reviewer_dissent']),2)
        self.assertEqual(result['disagreements'][0]['kind'],'between_reviewers')

    def test_native_metrics_link_confirmed_message_and_same_revision(self):
        # All rows remain local in memory. Use a synthetic non-test project to exercise the production join.
        from harness_runtime import initialize
        init=initialize(self.state, {'project_id':'LAB-METRIC','project_name':'Simulação local','episode_title':'Teste',
                        'episode_id':'M-EP1','target_seconds':60},{**self.auth,'op_id':'METRIC-INIT'})['candidate']
        target=next(r for r in init['tables']['Episodes'] if r['id']=='M-EP1')
        schema=load('schemas/shared-state.tables.json')['tables']
        def row(table,key,**args):
            record={k:'' for k in schema[table]['columns']}
            record.update(id=key,project_id='LAB-METRIC',episode_id='M-EP1',revision=1,is_test=False,
                          updated_at=init['read_at'],updated_by='Simulator',last_op_id='TEST-LOCAL',status='DRAFT')
            record.update(args);init['tables'][table].append(record);return record
        common=dict(target_table='Episodes',target_id=target['id'],target_revision=1)
        ev=row('Evaluation Results','EV-T',**common,rubric_ref='rubric-a',reviewer='agent-a',evidence='media',
               decision='READY_FOR_HUMAN_DECISION')
        fb=row('Human Feedback','HF-T',**common,evaluation_id=ev['id'],human_decision='REJECT',
               user_message_ref='test-message-resolved-in-memory',reason='Incompatível com a intenção',
               evidence='quadro 12',preference_scope='episode')
        self.assertEqual(native_metrics(init,[])['excluded'][0]['reason'],'unconfirmed_message_origin')
        res=native_metrics(init,[fb['user_message_ref']]);self.assertEqual(res['real_human_n'],1)
        self.assertEqual(res['false_approval_rate'],1.0)
        target['revision']=2;fb['target_revision']=2
        self.assertEqual(native_metrics(init,[fb['user_message_ref']])['excluded'][0]['reason'],'evaluation_scope_or_version_mismatch')

    def test_genre_cases_recovered_only_for_matching_department(self):
        c=load('knowledge/genre-cases.json')[0]
        spec={'department':c['departments'][0],'context':{'genre':c['genre']},
              'target':{'path':str(ROOT/'examples/takes/COM-01-pair.json'),'id':'test-case','revision':1}}
        self.assertIn(c['case_id'],[v['case_id'] for v in review_packet(spec)['genre_cases']])
        spec['holdout']=True
        self.assertEqual(review_packet(spec)['genre_cases'],[])

if __name__=='__main__':unittest.main()
