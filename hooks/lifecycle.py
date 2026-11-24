"""CPE lifecycle reminders and minimal receipts, with no production data or transcript capture."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from cpe_hook import handle as pretool

START_EVENTS={'SessionStart','SubagentStart'}
CONTEXT_EVENTS={'UserPromptSubmit','PreCompact','PostCompact','SubagentStop','Stop'}
RECEIPT_EVENTS={'PostToolUse','SessionEnd','Interrupt'}


def contextual(event,text):
    return {'hookSpecificOutput':{'hookEventName':event,'additionalContext':text}}


def handle(payload):
    event=payload.get('hook_event_name')
    if event=='PreToolUse':
        return pretool(payload)
    if event in START_EVENTS:
        return contextual(event,'For a CPE production request, load cinematic-production-engine/SKILL.md and the local host setup. Use current shared state, scoped human decisions and readback receipts.')
    if event=='UserPromptSubmit':
        prompt=payload.get('prompt','')
        if isinstance(prompt,str) and re.search(r'cinematic.production.engine|\bcpe\b|skill de cinema',prompt,re.I):
            return contextual(event,'Present the relevant CPE support panel in this conversation. Read the connected project state before production advice. A local HTML click is a draft until communicated and validated.')
        return {}
    if event in {'PreCompact','PostCompact'}:
        return contextual(event,'CPE continuity comes from the configured project, saved artifact versions and a fresh native state read. Do not infer persistence from a tool success or transfer synthetic preferences to production.')
    if event in {'SubagentStop','Stop'}:
        return contextual(event,'If this turn used CPE, preserve rejection and UNKNOWN results. Report the observed artifact, scope and remaining human review. A comparative winner does not imply artistic approval.')
    return {}


def receipt(payload,root=None):
    # The user can set a private destination. Store event metadata only, never prompt, result or transcript.
    destination=root or os.environ.get('CPE_HOOK_RECEIPTS')
    if not destination:return None
    folder=Path(destination).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    session=str(payload.get('session_id','unknown'))
    token=hashlib.sha256(session.encode()).hexdigest()[:20]
    record={'event':payload.get('hook_event_name'),'session_digest':token,
            'observed_at_ns':time.time_ns(),'tool_name':str(payload.get('tool_name',''))[:180],
            'production_readback_verified':False}
    # A separate exclusive file per invocation avoids concurrent append truncation.
    target=folder/(token+'-'+str(record['observed_at_ns'])+'-'+str(os.getpid())+'.json')
    with target.open('x',encoding='utf8') as stream:json.dump(record,stream,separators=(',',':'))
    return target


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipts',type=Path)
    args=parser.parse_args()
    try:
        payload=json.load(sys.stdin)
        if not isinstance(payload,dict):raise ValueError('Expected object')
        result=handle(payload)
        if payload.get('hook_event_name') in RECEIPT_EVENTS:receipt(payload,args.receipts)
    except Exception:
        # Advisory lifecycle events never fabricate a successful production state.
        result={'systemMessage':'CPE hook could not process this event. Verify production state explicitly.',
                'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny',
                'permissionDecisionReason':'CPE could not validate this hook input.'}}
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
