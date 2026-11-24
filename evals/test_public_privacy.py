import copy,hashlib,json,sys,tempfile,unittest,zipfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'hooks')]
from privacy_scan import scan
from local_binding import load_binding
from study_feedback import record_feedback,comparison_metrics
from lifecycle import handle,receipt

class PublicPrivacyTests(unittest.TestCase):
    def test_scanner_inspects_nested_archives(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with zipfile.ZipFile(root/'fixture.zip','w') as archive:
                archive.writestr('private.txt','docs.google.com/spreadsheets/d/'+'x'*44)
            self.assertEqual(scan(root)['status'],'REVIEW_REQUIRED')
            self.assertTrue(any('!private.txt' in x['file'] for x in scan(root)['findings']))
    def test_public_seed_cannot_supply_a_director_preference(self):
        seed=json.loads((ROOT/'templates/library-seed.json').read_text(encoding='utf8'))
        self.assertEqual(seed['tables']['Creative Preferences'],[])

    def test_synthetic_binding_is_valid_and_private_override_takes_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'integrations').mkdir()
            base=json.loads((ROOT/'integrations/google-sheets.binding.json').read_text(encoding='utf8'))
            (root/'integrations/google-sheets.binding.json').write_text(json.dumps(base),encoding='utf8')
            self.assertEqual(load_binding(root),base)
            base['spreadsheet_id']='OTHER-LOCAL-FIXTURE'
            (root/'integrations/local-binding.json').write_text(json.dumps(base),encoding='utf8')
            self.assertEqual(load_binding(root)['spreadsheet_id'],'OTHER-LOCAL-FIXTURE')
            self.assertEqual(load_binding(root)['spreadsheet_url'],'https://docs.google.com/spreadsheets/d/OTHER-LOCAL-FIXTURE/edit')
            (root/'integrations/local-binding.json').write_text('{}',encoding='utf8')
            with self.assertRaises(ValueError):load_binding(root)
    def test_hook_migration_preserves_existing_group_without_losing_the_new_matcher(self):
        from configure_hooks import definitions
        wanted=definitions()['hooks']['PreToolUse'][0]
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'hooks.json'
            different=copy.deepcopy(wanted)
            different['matcher']='^unrelated-only$'
            different['hooks'][0]['timeout']=99
            original={'hooks':{'PreToolUse':[different]}}
            target.write_text(json.dumps(original),encoding='utf8')
            subprocess.run([sys.executable,'-B',str(ROOT/'scripts/configure_hooks.py'),'--output',str(target)],check=True,capture_output=True)
            merged=json.loads(target.read_text(encoding='utf8'))
            self.assertEqual(merged['hooks']['PreToolUse'],[different,wanted])
            self.assertEqual(json.loads(target.with_name('hooks.json.before-cpe').read_text(encoding='utf8')),original)
    def test_feedback_is_private_immutable_and_never_production_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'frame.txt';path.write_text('frame version one',encoding='utf8')
            spec={'authorized':True,'actor':'test director','message_ref':'synthetic human-message fixture',
                  'decision':'BOTH_FAIL','reason':'Test label only','study_id':'fixture',
                  'materials':[{'id':'A','path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}
            first=record_feedback(spec,folder)
            self.assertEqual(first,record_feedback(spec,folder))
            self.assertFalse(first['production_approval'])
            changed={**spec,'decision':'A'}
            with self.assertRaises(ValueError):record_feedback(changed,folder)
            path.write_text('different frame',encoding='utf8')
            with self.assertRaises(ValueError):record_feedback(spec,folder)
    def test_preference_disagreement_does_not_fabricate_false_approval_metric(self):
        result=comparison_metrics(['A','A'],'BOTH_FAIL')
        self.assertEqual(result['pairwise_agreement'],0)
        self.assertIsNone(result['artistic_approval_rate'])
        self.assertFalse(result['generalization_measured'])
    def test_lifecycle_reminders_never_claim_native_persistence(self):
        for event in ['SessionStart','UserPromptSubmit','PreCompact','PostCompact','Stop','SubagentStop']:
            result=handle({'hook_event_name':event,'prompt':'Use CPE'})
            self.assertIn('hookSpecificOutput',result)
        self.assertEqual(handle({'hook_event_name':'UserPromptSubmit','prompt':'unrelated'}),{})
        blocked=handle({'hook_event_name':'PreToolUse','tool_name':'mcp__codex_apps__higgsfield_generate_video'})
        self.assertEqual(blocked['hookSpecificOutput']['permissionDecision'],'deny')
    def test_native_hook_receipt_does_not_store_prompt_result_or_transcript(self):
        with tempfile.TemporaryDirectory() as folder:
            payload={'hook_event_name':'PostToolUse','session_id':'example','prompt':'private',
                     'tool_result':'private','transcript_path':'private','tool_name':'fixture'}
            file=receipt(payload,folder);result=json.loads(file.read_text(encoding='utf8'))
            self.assertFalse(result['production_readback_verified'])
            self.assertNotIn('private',file.read_text(encoding='utf8'))

if __name__=='__main__':unittest.main()
