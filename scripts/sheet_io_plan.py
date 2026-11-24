"""Bounded connector read plan and reconstruction. No Google API client or credentials."""
import datetime as dt
from shared_state import SCHEMA,require,validate,StateError
def letters(n):
 value=''
 while n:n,r=divmod(n-1,26);value=chr(65+r)+value
 return value
def read_plan(metadata,binding,page_rows=200):
 require(type(page_rows) is int and 1<=page_rows<=1000,'Invalid read page size');sheets={s['properties']['title']:s['properties'] for s in metadata['sheets']};pages=[]
 require(metadata['spreadsheetId']==binding['spreadsheet_id'],'Metadata binding mismatch')
 for name,spec in SCHEMA['tables'].items():
  require(name in sheets,'Missing sheet '+name);p=sheets[name];require(p['sheetId']==binding['sheet_ids'][name],'Sheet replaced/rebound: '+name);rows=p['gridProperties']['rowCount'];cols=len(spec['columns']);require(p['gridProperties']['columnCount']>=cols,'Grid missing schema columns')
  for start in range(0,rows,page_rows):
   end=min(start+page_rows,rows);pages.append({'sheet_name':name,'start_row_index':start,'end_row_index':end,'range':f'A{start+1}:{letters(cols)}{end}','value_render_option':'UNFORMATTED_VALUE'})
 return {'spreadsheet_id':binding['spreadsheet_id'],'pages':pages,'grid_bounds':{n:sheets[n]['gridProperties']['rowCount'] for n in SCHEMA['tables']},'complete_grid_read':True,'scope_filter_after_reconstruction':True,'note':'Re-read metadata after reconstruction; changed bounds/IDs require retry. No atomicity.'}
def reconstruct(plan,page_values,scope,read_at):
 require(len(page_values)==len(plan['pages']),'Incomplete read pages');tables={n:[] for n in SCHEMA['tables']};headers={};source_rows={name:{} for name in SCHEMA["tables"]}
 for name in tables:
  cursor=0
  for page in [p for p in plan['pages'] if p['sheet_name']==name]:require(page['start_row_index']==cursor and page['end_row_index']>cursor,'Read page gap/duplicate');cursor=page['end_row_index']
  require(cursor==plan['grid_bounds'][name],'Grid tail omitted: '+name)
 for page,values in zip(plan['pages'],page_values):
  name=page['sheet_name'];cols=SCHEMA['tables'][name]['columns'];require(len(values)<=page['end_row_index']-page['start_row_index'],'Unexpected page length')
  for offset,values_row in enumerate(values):
   rownum=page['start_row_index']+offset
   if rownum==0:require(values_row==cols,'Header mismatch '+name);headers[name]=True;continue
   require(len(values_row)<=len(cols),'Unknown columns in row');row={k:values_row[i] if i<len(values_row) else '' for i,k in enumerate(cols)}
   if not row['id']:
    populated=[k for k,v in row.items() if v!='' and not(v is False and SCHEMA['tables'][name]['types'][k]=='boolean')]
    require(not populated,'Orphan populated row without ID: '+name+' row '+str(rownum+1));continue
   source_rows[name][row["id"]]=rownum+1
   tables[name].append(row)
 require(set(headers)==set(tables),'Missing headers');snapshot={'schema_version':'3.1.0','spreadsheet_id':plan['spreadsheet_id'],'read_at':read_at,'scope':scope,'tables':tables,'source_rows':source_rows};validate(snapshot);return snapshot
