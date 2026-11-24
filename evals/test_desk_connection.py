"""Connection regressions for queue typing, draft rebasing and missing episode anchors."""
import copy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'examples/connected-desk')]
from desk_queue import HEADERS,attach_intake,projection,material_for
from harness_runtime import validate_panel_base
from journal import journal_rows
from rehearsal import NAME,PROJECT,EP1,EP2,seed
from shared_state import SCHEMA,StateError,fingerprint,guard,validate


class DeskConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.at='2026-01-15T10:00:00Z'
        cls.empty={'schema_version':'3.1.0','spreadsheet_id':'test-native','read_at':cls.at,
                   'scope':{'project_id':PROJECT,'episode_id':EP2,'include_test':True},
                   'tables':{table:[] for table in SCHEMA['tables']}}
        cls.plan=seed(cls.empty,cls.at)
        cls.base=cls.plan['candidate']

    def test_duplicated_or_missing_ticket_isolated_by_episode(self):
        values=[HEADERS,['PED-001',NAME,2,'SH06','Som','Anna'],
                ['PED-002',NAME,'EP2','SH05','Outro','Bia'],
                ['PED-002','OUTRA','EP2','SH05','Duplicado','Bia'],
                ['',NAME,2,'SH06','Sem protocolo','Bia']]
        s=attach_intake(self.base,values)
        rows=projection(s,PROJECT,EP2)['queue']
        self.assertEqual([r['status'] for r in rows],['PROPOSTA','CONFLITO','CONFLITO'])
        self.assertEqual(s['desk_intake'][0]['source_values'][2],2)
        self.assertEqual(rows[0]['shot_id'],PROJECT+'-SH06')
        self.assertNotIn('Duplicado',str(rows))
        self.assertEqual(s['desk_intake'][0]['sha256'],fingerprint(values[1]))

    def test_row_movement_preserves_ticket_fingerprint(self):
        raw=['PED-003',NAME,'EP2','SH02','Continuidade','Teste']
        one=attach_intake(self.base,[HEADERS,raw])['desk_intake'][0]
        two=attach_intake(self.base,[HEADERS,['PED-001'],raw])['desk_intake'][0]
        self.assertNotEqual(one['row'],two['row'])
        self.assertEqual(one['sha256'],two['sha256'])

    def test_human_names_and_unfinished_rows(self):
        s=attach_intake(self.base,[HEADERS,['PED-009','A ultima agua · ensaio de direcao','Episódio 02','sh06','Rever a buzina','Som'],
                                   ['PED-011',NAME,'EP2','SH04','  ','Montagem']])
        queue=projection(s,PROJECT,EP2)['queue']
        self.assertEqual([r['ticket'] for r in queue],['PED-009'])

    def test_target_by_screenplay_title(self):
        target=material_for(self.base,PROJECT,EP2,'A volta à estação')
        self.assertEqual(target['table'],'Screenplays')
        with self.assertRaises(StateError):
            material_for(self.base,PROJECT,EP1,'A volta à estação')

    def test_prepared_can_reserve_new_project_and_episode(self):
        s=copy.deepcopy(self.empty)
        events=journal_rows(self.plan,'PREPARED',PROJECT,EP2,True,self.at,'ensaio')
        s['tables']['Revision History']=events
        self.assertTrue(validate(s))
        s['tables']['Revision History']=[{**e,'event':'CONFIRMED'} for e in events]
        with self.assertRaises(StateError):validate(s)

    def test_prepared_with_wrong_episode_refused(self):
        s=copy.deepcopy(self.empty)
        s['tables']['Revision History']=journal_rows(self.plan,'PREPARED',PROJECT,'DIFERENTE',True,self.at,'ensaio')
        with self.assertRaises(StateError):validate(s)

    def test_rebase_distinguishes_unrelated_from_relevant(self):
        original=copy.deepcopy(self.base)
        original['scope']['episode_id']=EP1
        message={'spreadsheet_id':original['spreadsheet_id'],'scope':original['scope'],
                 'authorized':True,'base_scope_sha256':fingerprint(guard(original))}
        fresh=copy.deepcopy(original)
        fresh['tables']['Screenplays'][0]['text_or_ref']+='Nova fala no EP2.'
        self.assertTrue(validate_panel_base(message,fresh,original)['rebased_after_unrelated_change'])
        fresh['tables']['Projects'][0]['name']+=' (mudou)'
        with self.assertRaises(StateError):validate_panel_base(message,fresh,original)

