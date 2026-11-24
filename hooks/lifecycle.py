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
RECEIPT_EVENTS={'PostToolUse','SessionEnd','Interrupt','PreCompact','PostCompact','SubagentStop','Stop'}


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
    event=None
    try:
        payload=json.load(sys.stdin)
        if not isinstance(payload,dict):raise ValueError('Expected object')
        event=payload.get('hook_event_name')
        result=handle(payload)
        if event in RECEIPT_EVENTS:receipt(payload,args.receipts)
    except Exception:
        result={'systemMessage':'CPE hook could not process this event. Verify production state explicitly.'}
        if event=='PreToolUse':
            result['hookSpecificOutput']={'hookEventName':'PreToolUse','permissionDecision':'deny',
                                          'permissionDecisionReason':'CPE could not validate this hook input.'}
        elif event=='SessionEnd':
            print(result['systemMessage'],file=sys.stderr)
            return 1
    print(json.dumps(result,ensure_ascii=False))
    return 0


if __name__=='__main__':raise SystemExit(main())
