import unittest,sys,json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from sheet_io_plan import *
class SheetReadPlan(unittest.TestCase):
 def setup_values(self):
  s=json.loads((R/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'));binding={'spreadsheet_id':s['spreadsheet_id'],'sheet_ids':{n:i for i,n in enumerate(SCHEMA['tables'])}};metadata={'spreadsheetId':s['spreadsheet_id'],'sheets':[{'properties':{'title':n,'sheetId':i,'gridProperties':{'rowCount':1201,'columnCount':52}}} for i,n in enumerate(SCHEMA['tables'])]};p=read_plan(metadata,binding,200);raw={n:[spec['columns']]+[[r[k] for k in spec['columns']] for r in s['tables'][n]] for n,spec in SCHEMA['tables'].items()};values=[raw[pg['sheet_name']][pg['start_row_index']:pg['end_row_index']] for pg in p['pages']];return s,p,values
 def test_growth_over_1000_not_omitted(self):
  s,p,v=self.setup_values();self.assertTrue(any(x['end_row_index']==1201 for x in p['pages']));r=reconstruct(p,v,s['scope'],s['read_at']);self.assertEqual(r['tables'],s['tables'])
 def test_missing_page_rejected(self):
  s,p,v=self.setup_values();self.assertRaises(StateError,reconstruct,p,v[:-1],s['scope'],s['read_at'])
 def test_orphan_row_not_silently_dropped(self):
  s,p,v=self.setup_values();i=next(i for i,pg in enumerate(p['pages']) if pg['sheet_name']=='Projects' and pg['start_row_index']==200);v[i]=[['','','','','','','', '','orphan name']];self.assertRaises(StateError,reconstruct,p,v,s['scope'],s['read_at'])
if __name__=='__main__':unittest.main()
