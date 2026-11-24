import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import desk_connector as connector
from shared_state import StateError


def cell(value):
    kind='boolValue' if type(value) is bool else 'numberValue' if type(value) in (int,float) else 'stringValue'
    return {'effectiveValue':{kind:value}} if value!='' else {}


class NativeReadCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=json.loads((ROOT/'templates/shared-state.test-fixture.json').read_text(encoding='utf-8'))
        binding=connector.BINDING
        raw={name:[spec['columns']]+[[r[k] for k in spec['columns']] for r in cls.state['tables'][name]]
             for name,spec in connector.SCHEMA['tables'].items()}
        raw[connector.INBOX]=[connector.HEADERS]+[[]]*8+[['PED-802','Série','EP2','SH06','ouvir B','montagem']]
        properties={n:{'title':n,'sheetId':binding['sheet_ids'].get(n,connector.INBOX_ID),
                    'gridProperties':{'rowCount':max(20,len(rows)+2),'columnCount':max(26,len(rows[0]))}}
                    for n,rows in raw.items()}
        # Ignore the display-only dashboard when matching production schema.
        meta={'spreadsheetId':binding['spreadsheet_id'],'sheets':[{'properties':p} for p in properties.values()]}
        before={'account':binding['account'],'link_id':'conexao-autenticada','observed_at':'2026-11-24T12:00:00Z','response':meta}
        after={**before,'observed_at':'2026-11-24T12:01:00Z','response':copy.deepcopy(meta)}
        spec={'before':before,'after':after,'scope':cls.state['scope'],'page_rows':8}
        grid,plan,pages=connector.plan_parts(spec)
        calls=connector.batches_for(pages,before['link_id'])
        evidence=[]
        for call,group in calls:
            items=[]
            for page in group:
                n=page['sheet_name']
                start=page['start_row_index']
                rows=raw[n][start:page['end_row_index']]
                block={'startRow':start} if start else {}
                if rows:
                    block['rowData']=[{'values':[cell(v) for v in row]} if row else {} for row in rows]
                items.append({'properties':properties[n],'data':[block]})
            evidence.append({**before,'observed_at':'2026-11-24T12:00:30Z','index':call['index'],
                        'tool':connector.CELLS,'ranges':call['arguments']['ranges'],'response':{
                            'spreadsheetId':meta['spreadsheetId'],'sheets':list(reversed(items))}})
        cls.spec={**spec,'batches':list(reversed(evidence))}

    def test_native_roundtrip_rows_typed_values_and_sparse_queue(self):
        plan=connector.dispatch('desk-read-plan',self.spec)
        self.assertTrue(all(1<=len(c['arguments']['ranges'])<=5 and c['arguments']['cell_fields']=='effectiveValue' for c in plan['batches']))
        state=connector.dispatch('desk-read-copy',self.spec)
        self.assertEqual(state['tables'],self.state['tables'])
        self.assertEqual(state['desk_intake'][0]['row'],10)
        self.assertEqual(state['source_rows']['Projects'][state['tables']['Projects'][0]['id']],2)
        self.assertFalse(state['read_provenance']['atomic'])
        self.assertFalse(state['read_provenance']['remote_read_performed_by_cli'])
        self.assertEqual(state['read_at'],self.spec['after']['observed_at'])

    def test_changes_to_binding_grid_or_file_version_require_retry(self):
        for field in ('rowCount','columnCount','sheetId','account','spreadsheetId','drive_version'):
            spec=copy.deepcopy(self.spec)
            after=spec['after']
            props=after['response']['sheets'][0]['properties']
            if field in {'rowCount','columnCount'}:
                props['gridProperties'][field]+=1
            elif field=='sheetId':
                props[field]+=1
            elif field=='spreadsheetId':
                after['response'][field]='outra-planilha'
            else:
                after[field]='origem-diferente'
            with self.subTest(field=field),self.assertRaises(StateError):
                connector.dispatch('desk-read-copy',spec)

    def test_missing_duplicate_wrong_range_or_untrusted_source_is_refused(self):
        changes=['missing','duplicate','wrong_range','bad_connection','foreign_sheet','old_batch','duplicate_sheet',
                 'misaligned_rows','missing_block','malformed_value','wrong_fields']
        for change in changes:
            spec=copy.deepcopy(self.spec)
            batch=next(b for b in spec['batches'] if b['index']==0)
            sheet=batch['response']['sheets'][0]
            if change=='missing':spec['batches'].pop()
            if change=='duplicate':spec['batches'][0]['index']=spec['batches'][1]['index']
            if change=='wrong_range':batch['ranges'][0]="'Projects'!A1:A1"
            if change=='bad_connection':batch['link_id']='outra-conexao'
            if change=='foreign_sheet':batch['response']['spreadsheetId']='outra-planilha'
            if change=='old_batch':batch['observed_at']='2025-01-01T00:00:00Z'
            if change=='duplicate_sheet':batch['response']['sheets'].append(sheet)
            if change=='misaligned_rows':sheet['data'][0]['startRow']=7
            if change=='missing_block':sheet['data']=[]
            if change=='malformed_value':sheet['data'][0]['rowData'][0]['values'][0]={'formattedValue':'id'}
            if change=='wrong_fields':batch['cell_fields']='formattedValue'
            with self.subTest(change=change),self.assertRaises(ValueError):
                connector.dispatch('desk-read-copy',spec)

    def test_errored_formula_and_non_textual_queue_cells_are_explicit_failures(self):
        with self.assertRaises(ValueError):
            connector.cell_value({'effectiveValue':{'errorValue':{'type':'REF'}}})
        spec=copy.deepcopy(self.spec)
        for batch in spec['batches']:
            for sheet in batch['response']['sheets']:
                if sheet['properties']['title']==connector.INBOX and sheet['data'][0].get('startRow')==8:
                    sheet['data'][0]['rowData'][1]['values'][2]=cell(2)
        with self.assertRaisesRegex(StateError,'campo não textual'):
            connector.dispatch('desk-read-copy',spec)
