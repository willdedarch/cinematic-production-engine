"""Fresh synthetic journals for backward-compatibility tests, with no account exports."""
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shared_state import prepare
from journal import journal_rows


def fixture_pair(name='link-repair-plan'):
    state=json.loads((ROOT/'templates/shared-state.test-fixture.json').read_text(encoding='utf8'))
    # This isolated scope deliberately differs from the mutation used in the scope regression.
    state=json.loads(json.dumps(state).replace('TEST-CPE31','PUBLIC-FIXTURE'))
    state['spreadsheet_id']='PUBLIC-SYNTHETIC-SHEET'
    state['tables']['Revision History']=[]
    project=state['tables']['Projects'][0]['id']
    episode=state['tables']['Episodes'][0]['id']
    target=state['tables']['Decisions'][0]['id']
    def edit(before,op,at,choice):
        revision=next(r['revision'] for r in before['tables']['Decisions'] if r['id']==target)
        return prepare(before,{'op_id':op,'actor':'synthetic-fixture-author','authorized':True,
            'user_message_ref':'Synthetic compatibility fixture; no human approval or remote write',
            'at':at,'changes':[{'table':'Decisions','id':target,'expected_revision':revision,
                               'values':{'choice':choice,'status':'RECORDED'}}]})
    def confirmed(plan,prepared_at,confirmed_at,read_at):
        after=copy.deepcopy(plan['candidate'])
        after['tables']['Revision History'].extend(
            journal_rows(plan,'PREPARED',project,episode,True,prepared_at,'synthetic://fixture')+
            journal_rows(plan,'CONFIRMED',project,episode,True,confirmed_at,'synthetic://fixture'))
        after['read_at']=read_at
        return after
    first=edit(state,'PUBLIC-BASELINE','2026-11-24T00:05:00Z','baseline')
    state=confirmed(first,'2026-11-24T00:06:00Z','2026-11-24T00:07:00Z','2026-11-24T00:08:00Z')
    plan=edit(state,'PUBLIC-'+name.upper(),'2026-11-24T00:10:00Z','new value')
    final=confirmed(plan,'2026-11-24T00:11:00Z','2026-11-24T00:12:00Z','2026-11-24T00:13:00Z')
    # 1.1 stores the baseline in candidate instead of the later history_baseline field.
    plan.pop('history_baseline',None)
    return plan,final
