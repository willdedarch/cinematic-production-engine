import unittest,sys,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class Hooks(unittest.TestCase):
 def run_hook(self,name):
  r=subprocess.run([sys.executable,str(R/'hooks/cpe_hook.py')],input=json.dumps({'hook_event_name':'PreToolUse','tool_name':name}),text=True,capture_output=True,check=True);return json.loads(r.stdout)
 def test_paid_generation_denied(self):self.assertEqual(self.run_hook('mcp__codex_apps__higgsfield_generate_video')['hookSpecificOutput']['permissionDecision'],'deny')
 def test_unknown_higgs_denied(self):self.assertEqual(self.run_hook('mcp__future_higgsfield_unknown')['hookSpecificOutput']['permissionDecision'],'deny')
 def test_unverified_namespace_cannot_spoof_read_suffix(self):self.assertEqual(self.run_hook('mcp__unverified_higgsfield_models_get')['hookSpecificOutput']['permissionDecision'],'deny')
 def test_catalog_read_allowed(self):self.assertEqual(self.run_hook('mcp__codex_apps__higgsfield_models_get'),{})
 def test_unmatched_tool_not_claimed_controlled(self):self.assertEqual(self.run_hook('other_tool'),{})
 def test_template_not_active_paths(self):
  data=json.loads((R/'hooks/hooks.example.json').read_text(encoding='utf-8'));self.assertIn('ABSOLUTE',data['hooks']['PreToolUse'][0]['hooks'][0]['command'])
if __name__=='__main__':unittest.main()
