"""Optional direct Higgsfield pre-tool guard. Not installed or a universal enforcement boundary."""
import json,sys
READ_ALLOWLIST={'mcp__codex_apps__higgsfield_models_get','mcp__codex_apps__higgsfield_models_search','mcp__codex_apps__higgsfield_get_preset_instructions','mcp__codex_apps__higgsfield_get_presets'}
def handle(payload):
 if payload.get('hook_event_name')!='PreToolUse':return {'systemMessage':'CPE: consult current shared state and policies before the production step.'}
 name=payload.get('tool_name','')
 if 'higgsfield' not in name:return {}
 if name in READ_ALLOWLIST:return {}
 return {'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':'CPE prohibits paid/unknown-cost Higgsfield operations. Only the verified read-only catalog/workflow allowlist is supported by this hook.'}}
def main():
 try:payload=json.load(sys.stdin);result=handle(payload)
 except Exception:result={'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':'CPE could not validate this matched hook input.'}}
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
