"""Prepare exact user-reviewed Codex hook definitions without changing trust records."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys

EVENTS=('SessionStart','UserPromptSubmit','PreToolUse','PostToolUse','PreCompact','PostCompact',
        'SubagentStart','SubagentStop','Stop','SessionEnd','Interrupt')
ROOT=Path(__file__).resolve().parents[1]


def hook_arguments(python, receipts):
    arguments=[str(python),str(ROOT/'hooks/lifecycle.py')]
    if receipts:
        arguments.extend(['--receipts',str(Path(receipts).resolve())])
    return arguments


def hook_command(arguments, *, windows):
    if windows:
        quotes = str.maketrans({quote: quote * 2 for quote in "'‘’‚‛"})
        literals = ["'" + argument.translate(quotes) + "'" for argument in arguments]
        return '& ' + ' '.join(literals)
    return shlex.join(arguments)


def definitions(python=sys.executable,receipts=None):
    command=hook_command(hook_arguments(python, receipts), windows=sys.platform == 'win32')
    groups={event:[{'hooks':[{'type':'command','command':command,'timeout':3}]}] for event in EVENTS}
    groups['PreToolUse'][0]['matcher']='^mcp__.*higgsfield.*'
    return {'description':'CPE lifecycle context. Exact definitions require review and trust in the host.',
            'hooks':groups}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--receipts',type=Path)
    args=parser.parse_args()
    new=definitions(receipts=args.receipts)
    legacy_command=subprocess.list2cmdline(hook_arguments(sys.executable, args.receipts))
    output=args.output.resolve()
    current=json.loads(output.read_text(encoding='utf8')) if output.exists() else {}
    if not isinstance(current.get('hooks',{}),dict):raise ValueError('Unknown existing hook configuration')
    merged=json.loads(json.dumps(current))
    merged.setdefault('hooks',{})
    for event,groups in new['hooks'].items():
        old=merged['hooks'].setdefault(event,[])
        for group in groups:
            legacy_group={**group, 'hooks':[dict(handler, command=legacy_command) for handler in group['hooks']]}
            if legacy_group != group and legacy_group in old:
                if group in old:
                    old.remove(legacy_group)
                else:
                    old[old.index(legacy_group)] = group
            elif group not in old:
                old.append(group)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        backup=output.with_name(output.name+'.before-cpe')
        if backup.exists():raise ValueError('Backup already exists; inspect before editing configuration')
        backup.write_bytes(output.read_bytes())
    output.write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'configuration':str(output),'trust_modified':False,'review_required':True,
                      'scope':'Lifecycle hooks; no universal interception claim'}))


if __name__=='__main__':main()
