"""Chunk large native Sheets journal cells; no network or persistence."""
import json
from shared_state import canonical,fingerprint,require
from journal_codec import change_payloads, cell_units, CELL_BUDGET
def journal_rows(plan,event,project_id,episode_id,is_test,at,evidence_ref):
 require(event in {'PREPARED','CONFIRMED','INCOMPLETE','CONFLICT'},'Unknown journal event')
 payloads=change_payloads(plan['changes'])
 require(all(cell_units(payload)<=CELL_BUDGET for payload in payloads),'Journal cell budget exceeded')
 rows=[]
 for i,payload in enumerate(payloads,1):
  rows.append(dict(id=plan['op_id']+'-'+event+'-'+str(i),project_id=project_id,episode_id=episode_id,revision=1,updated_at=at,updated_by=plan['actor'],is_test=is_test,last_op_id=plan['op_id'],op_id=plan['op_id'],event=event,actor=plan['actor'],authorization_ref=plan['authorization_ref'],changes_json=payload,guards_json=canonical({'algorithm':'sha256-canonical','digest':fingerprint(plan['guards'])}),result='Journal event; only independent readback can confirm persistence; atomic=false',evidence_ref=evidence_ref))
 return rows
