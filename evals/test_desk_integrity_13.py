"""End-to-end authorization, version links and recoverable alternate sound edits."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))

from desk_pairs import dispatch as pair_command
from desk_queue import PROPOSAL, RESULT, HEADERS, dispatch, attach_intake, receipt
from desk_variant import materialize
from journal import journal_rows
from shared_state import StateError, canonical, check_guards, fingerprint, index, prepare, validate
from shot_workflow import ref, link_change

class DeskIntegrity(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.ws=Path(temp.name)
        self.base=json.loads((ROOT/'examples/takes/demo-state.json').read_text(encoding='utf-8'))
        self.shot=self.base['tables']['Shot List'][0]
        self.a,self.b=self.base['tables']['Artifact Registry'][:2]
        self.scope={'project_id':self.shot['project_id'],'episode_id':self.shot['episode_id'],'include_test':True}
        self.msg='Ensaio de integridade da mesa'
        self.auth={'authorized':True,'actor':'Ensaio','user_message_ref':self.msg}
        self.s=self.link(self.base,self.shot,self.a)
        self.spec={**self.scope,'authorization':self.auth,'request':'Manter a pausa.','shot_id':self.shot['id'],
                   'media':ref('Artifact Registry',self.a)}

    def command(self,action,s,spec):return dispatch(action,s,spec,self.ws)
    def link(self,s,shot,asset):
        auth={**self.auth,'op_id':'TEST-LINK-'+shot['id']+asset['id'],'at':datetime.now(timezone.utc).isoformat()}
        spec={'relation':'take','decision_id':auth['op_id'],'authorization':auth,'reason':'Arquivo do plano'}
        return prepare(s,{**auth,'changes':[link_change(s,spec,ref('Shot List',shot),ref('Artifact Registry',asset))]})['candidate']

    def proposal(self,s=None,spec=None):
        return self.command('desk-propose',s or self.s,spec or self.spec)

    def resolve(self,plan,state=None,**overrides):
        state=state or plan['candidate']
        key=plan['desk_item_id']
        args={**self.scope,'authorization':self.auth,'proposal_id':key,
              'proposal_sha256':fingerprint(index(state)['Decisions'][key]),'choice':'accept','reason':'Prefiro a pausa.'}
        return self.command('desk-resolve',state,{**args,**overrides})

    def generic(self,s,rows):
        ignore={'id','revision','updated_at','updated_by','last_op_id'}
        changes=[{'id':r['id'],'table':'Decisions','expected_revision':None,'values':{k:v for k,v in r.items() if k not in ignore}} for r in rows]
        return prepare(s,{**self.auth,'at':datetime.now(timezone.utc).isoformat(),'op_id':'TEST-GENERIC','changes':changes})

    def test_candidate_pinned_on_accept_and_existing_selection_changes_conflict(self):
        first=self.proposal()
        s=self.link(first['candidate'],self.shot,self.b)
        other=self.proposal(s,{**self.spec,'media':ref('Artifact Registry',self.b),'request':'Experimentar B.'})
        accepted=self.resolve(first,other['candidate'])
        result=[c['after'] for c in accepted['changes'] if c['after']['topic']==RESULT][0]
        selected=[c['after'] for c in accepted['changes'] if c['after']['topic']!=RESULT][0]
        self.assertEqual(json.loads(selected['choice'])['to'],self.spec['media'])
        self.assertEqual(selected['last_op_id'],result['last_op_id'])
        with self.assertRaisesRegex(StateError,'selecionar'):self.generic(other['candidate'],[result])
        wrong=copy.deepcopy(selected);body=json.loads(wrong['choice']);body['to']=ref('Artifact Registry',self.b);wrong['choice']=canonical(body)
        with self.assertRaisesRegex(StateError,'selecionar'):self.generic(other['candidate'],[result,wrong])
        with self.assertRaisesRegex(StateError,'Conflito'):self.resolve(other,accepted['candidate'])
        rejected=self.resolve(other,accepted['candidate'],choice='reject')
        self.assertEqual(len(rejected['changes']),1)
        self.assertEqual(self.resolve(first,accepted['candidate'])['kind'],'EXISTING_DECISION')

    def test_generic_proposal_pins_auth_and_immutable_history(self):
        plan=self.proposal();row=plan['changes'][-1]['after']
        body=json.loads(row['choice'])
        self.assertTrue(any(p['table']=='Decisions' for p in body['pins']))
        insufficient=copy.deepcopy(body)
        insufficient['pins']=[p for p in body['pins'] if p['table']!='Decisions']
        with self.assertRaisesRegex(StateError,'Conflito'):
            self.generic(self.s,[{**row,'choice':canonical(insufficient)}])
        with self.assertRaisesRegex(StateError,'autorização'):
            self.generic(self.s,[{**row,'user_message_ref':'Outra mensagem'}])
        with self.assertRaisesRegex(StateError,'autor'):
            self.generic(self.s,[{**row,'choice':canonical({**body,'author':'Outra pessoa'})}])
        with self.assertRaisesRegex(StateError,'único plano'):
            self.generic(self.s,[{**row,'choice':canonical({**body,'target':self.spec['media']})}])
        with self.assertRaisesRegex(StateError,'immutable'):
            prepare(plan['candidate'],{**self.auth,'op_id':'TEST-MOD','at':datetime.now(timezone.utc).isoformat(),'changes':[
                {'id':row['id'],'table':'Decisions','expected_revision':1,'values':{'rationale':'Troca'}}]})
        with self.assertRaisesRegex(StateError,'outra versão'):
            self.proposal(plan['candidate'],{**self.spec,'media':ref('Artifact Registry',self.b)})

    def test_alternative_honors_file_bytes_and_rights(self):
        state=copy.deepcopy(self.base)
        asset=state['tables']['Artifact Registry'][0]
        p=self.ws/'pessoal.mp4';p.write_bytes((ROOT/asset['uri']).read_bytes());asset['uri']=str(p)
        s=self.link(state,self.shot,asset)
        plan=self.proposal(s,{**self.spec,'media':ref('Artifact Registry',asset)})
        p.write_bytes(b'outro trabalho')
        with self.assertRaisesRegex(StateError,'arquivo'):self.resolve(plan)
        asset['rights']='Sem autorização para montagem'
        restricted=self.link(state,self.shot,asset)
        with self.assertRaisesRegex(StateError,'direitos'):self.proposal(restricted,{**self.spec,'media':ref('Artifact Registry',asset)})

    def test_recoverable_local_edit_and_idempotence(self):
        spec={**self.spec,'source':self.spec['media'],'offset_ms':-400}
        spec.pop('media')
        original=(ROOT/self.a['uri']).read_bytes()
        plan=self.command('desk-edit',self.s,spec)
        media=next(c['after'] for c in plan['changes'] if c['table']=='Artifact Registry')
        asset=Path(media['uri']);before=asset.read_bytes();created=asset.stat().st_mtime_ns
        self.assertNotEqual(before,original)
        self.assertEqual((ROOT/self.a['uri']).read_bytes(),original)
        self.assertTrue(asset.with_name('origem.json').is_file())
        self.assertEqual(len(self.resolve(plan)['changes']),2)
        with patch('desk_variant.audio_shift',side_effect=AssertionError('A repetição tentou criar outro arquivo')):
            self.command('desk-edit',self.s,spec)
            retry=self.command('desk-edit',plan['candidate'],spec)
        self.assertEqual(retry['kind'],'EXISTING_PROPOSAL');self.assertEqual(asset.stat().st_mtime_ns,created)
        self.assertEqual(len(list((self.ws/'variantes').rglob('alternativa.mp4'))),1)
        with self.assertRaisesRegex(StateError,'outra versão'):
            self.command('desk-edit',plan['candidate'],{**spec,'offset_ms':200})

    def test_old_partial_local_file_preserved_on_recovery(self):
        key='TEST-ORFAO';origin={'source':ref('Artifact Registry',self.a),'offset_ms':-80}
        pending=self.ws/'variantes'/key;pending.mkdir(parents=True)
        old=pending/'alternativa.mp4';old.write_bytes(b'parcial da tentativa anterior')
        new=materialize(self.ws,key,ROOT/self.a['uri'],origin)
        self.assertNotEqual(old,new)
        self.assertEqual(old.read_bytes(),b'parcial da tentativa anterior')
        self.assertEqual(new,materialize(self.ws,key,ROOT/self.a['uri'],origin))
        new.write_bytes(b'outro arquivo')
        with self.assertRaisesRegex(StateError,'diverge'):
            materialize(self.ws,key,ROOT/self.a['uri'],origin)

    def test_pair_cannot_borrow_registered_take_from_another_shot(self):
        other={**self.shot,'id':'TEST-SH-OTHER','order':self.shot['order']+1}
        s=copy.deepcopy(self.base);s['tables']['Shot List'].append(other)
        args={**self.scope,'shot_id':self.shot['id'],'question':'Comparar estes arquivos?',
              'takes':[{'id':a['id'],'revision':a['revision']} for a in (self.a,self.b)]}
        pair=pair_command('desk-pair',s,args,self.ws)['manifest']
        s=self.link(s,other,self.a)
        with self.assertRaisesRegex(StateError,'outro plano'):pair_command('desk-pair',s,args,self.ws)
        with self.assertRaisesRegex(StateError,'outro plano'):
            pair_command('desk-vote',s,{**self.scope,'shot_id':self.shot['id'],'authorization':self.auth,'choice':'A',
                'pair_id':pair['pair_id'],'pair_sha256':pair['pair_sha256'],
                'start_ms':0,'mark_ms':1000,'end_ms':2000,'reason':'Mais silêncio','preference_scope':'shot'},self.ws)

    def test_handwritten_ticket_requires_unchanged_source_at_preparation_and_resolution(self):
        inputrow=['PED-TESTE-A',self.scope['project_id'],self.scope['episode_id'],self.shot['id'],'Diminuir a pausa.','Iara']
        s=attach_intake(self.s,[HEADERS,inputrow])
        plan=self.proposal(s,{**self.spec,'ticket':inputrow[0],'input_sha256':s['desk_intake'][0]['sha256']})
        row=plan['changes'][-1]['after']
        body=json.loads(row['choice'])
        with self.assertRaisesRegex(StateError,'colaborador'):self.generic(s,[{**row,'choice':canonical({**body,'author':'Outro nome'})}])
        with self.assertRaisesRegex(StateError,'fila'):self.generic(self.s,[row])
        result=self.resolve(plan,choice='reject')['changes'][0]['after']
        changed=attach_intake(plan['candidate'],[HEADERS,[*inputrow[:-1],'Outra pessoa']])
        with self.assertRaisesRegex(StateError,'fila'):self.generic(changed,[result])

    def test_receipt_requires_journal_and_every_target(self):
        first=self.proposal();plan=self.resolve(first)
        row=next(c['after'] for c in plan['changes'] if c['after']['topic']==RESULT)
        s=copy.deepcopy(plan['candidate'])
        self.assertFalse(receipt(s,row))
        now=datetime.now(timezone.utc);s['read_at']=(now+timedelta(seconds=3)).isoformat()
        for i,event in enumerate(['PREPARED','CONFIRMED']):
            s['tables']['Revision History'].extend(journal_rows(plan,event,self.scope['project_id'],self.scope['episode_id'],True,
                (now+timedelta(seconds=i)).isoformat(),'Ensaio'))
        self.assertEqual(receipt(s,row),plan['op_id'])
        s['tables']['Decisions']=[r for r in s['tables']['Decisions'] if not (r['last_op_id']==plan['op_id'] and r['id']!=row['id'])]
        self.assertFalse(receipt(s,row))
        with self.assertRaisesRegex(StateError,'selecionar'):validate(s)

    def test_fresh_prewrite_tracks_ticket_contents_not_row_number(self):
        inputrow=['PED-PRE',self.scope['project_id'],self.scope['episode_id'],self.shot['id'],'Antecipar o som.','Marta']
        s=attach_intake(self.s,[HEADERS,inputrow])
        p=self.proposal(s,{**self.spec,'ticket':inputrow[0],'input_sha256':s['desk_intake'][0]['sha256']})
        result=self.resolve(p)
        for plan,initial in [(p,s),(result,p['candidate'])]:
            fresh=copy.deepcopy(initial)
            now=datetime.now(timezone.utc)
            fresh['read_at']=(now+timedelta(seconds=2)).isoformat()
            fresh['tables']['Revision History'].extend(journal_rows(plan,'PREPARED',self.scope['project_id'],
                    self.scope['episode_id'],True,now.isoformat(),'Ensaio'))
            fresh['intake_values']=[HEADERS,[],inputrow]
            self.assertTrue(check_guards(plan,fresh,require_prepared=True))
            for newrows in ([HEADERS],[HEADERS,[*inputrow[:-1],'Outro autor']]):
                fresh['intake_values']=newrows
                with self.assertRaisesRegex(StateError,'fila'):
                    check_guards(plan,fresh,require_prepared=True)

    def test_legacy_shot_pin_suffices_for_identical_retry(self):
        plan=self.proposal()
        legacy=copy.deepcopy(plan['candidate'])
        p=index(legacy)['Decisions'][plan['desk_item_id']]
        data=json.loads(p['choice']);data.pop('target');p['choice']=canonical(data)
        same=self.proposal(legacy)
        self.assertEqual(same['kind'],'EXISTING_PROPOSAL')
        self.assertEqual(same['id'],p['id'])
        self.assertFalse(same['replay'])

    def test_historical_receipt_requires_complete_successor_chain(self):
        edit={**self.spec,'source':self.spec['media'],'offset_ms':120}
        edit.pop('media')
        p=self.command('desk-edit',self.s,edit)
        proposal=next(c['after'] for c in p['changes'] if c['table']=='Decisions' and c['after']['topic']==PROPOSAL)
        asset=next(c['after'] for c in p['changes'] if c['table']=='Artifact Registry')
        state=copy.deepcopy(p['candidate'])
        now=datetime.now(timezone.utc)
        def events(plan,state,seconds):
            for i,phase in enumerate(['PREPARED','CONFIRMED']):
                state['tables']['Revision History'].extend(journal_rows(plan,phase,self.scope['project_id'],self.scope['episode_id'],True,
                    (now+timedelta(seconds=seconds+i)).isoformat(),'Ensaio'))
            state['read_at']=(now+timedelta(seconds=seconds+2)).isoformat()
        events(p,state,0)
        change=prepare(state,{**self.auth,'at':(now+timedelta(seconds=3)).isoformat(),'op_id':'TEST-NOVA-REV','changes':[
            {'id':asset['id'],'table':'Artifact Registry','expected_revision':1,'values':{'origin':asset['origin']+' · revisão da ficha'}}]})
        latest=change['candidate']
        self.assertFalse(receipt(latest,proposal))
        events(change,latest,4)
        self.assertEqual(receipt(latest,proposal),p['op_id'])

if __name__=='__main__':unittest.main()

