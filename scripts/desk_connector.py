"""Plan and check native Sheets connector copies; this module does no network I/O."""
import json
import math
from pathlib import Path

from desk_queue import HEADERS, attach_intake
from sheet_io_plan import read_plan, reconstruct
from shared_state import SCHEMA, fingerprint, require, timestamp

from local_binding import load_binding
BINDING=load_binding()
INBOX='Fila de direção'
INBOX_ID=BINDING['sheet_ids'][INBOX]
METADATA='get_spreadsheet_metadata'
CELLS='get_spreadsheet_cells'


def metadata_grid(response):
    require(isinstance(response,dict) and response.get('spreadsheetId')==BINDING['spreadsheet_id'],
            'A leitura deve pertencer à planilha vinculada.')
    expected={name:BINDING['sheet_ids'][name] for name in SCHEMA['tables']}
    expected[INBOX]=INBOX_ID
    grid={}
    for sheet in response.get('sheets',[]):
        p=sheet['properties']
        name=p['title']
        if name not in expected:
            continue
        require(name not in grid and p['sheetId']==expected[name] and p.get('sheetType','GRID')=='GRID',
                'Aba duplicada, substituída ou incompatível: '+name)
        dims=p['gridProperties']
        rows,cols=dims['rowCount'],dims['columnCount']
        required=6 if name==INBOX else len(SCHEMA['tables'][name]['columns'])
        require(type(rows) is int and rows>=1 and type(cols) is int and cols>=required,'Dimensões inválidas em '+name)
        grid[name]=(p['sheetId'],rows,cols)
    require(set(grid)==set(expected),'Há abas ausentes na leitura de metadados.')
    return grid


def check_envelope(envelope, tool, link=None):
    require(isinstance(envelope,dict) and envelope.get('account','').casefold()==BINDING['account'].casefold(),
            'A conta de origem diverge do vínculo da produção.')
    link_id=envelope.get('link_id')
    require(isinstance(link_id,str) and bool(link_id.strip()) and (link is None or link==link_id),
            'Use a mesma conexão autenticada durante toda a leitura.')
    require(envelope.get('tool',tool)==tool,'A resposta foi atribuída a outra ferramenta.')
    observed=timestamp(envelope.get('observed_at'))
    require(isinstance(envelope.get('response'),dict) and envelope['response'].get('spreadsheetId')==BINDING['spreadsheet_id'],
            'Resposta nativa ausente ou de outra planilha.')
    return observed


def plan_parts(spec):
    before=spec['before']
    check_envelope(before,METADATA)
    grid=metadata_grid(before['response'])
    size=spec.get('page_rows',1000)
    plan=read_plan(before['response'],BINDING,size)
    pages=list(plan['pages'])
    queue_rows=grid[INBOX][1]
    for start in range(0,queue_rows,size):
        end=min(start+size,queue_rows)
        pages.append({'sheet_name':INBOX,'start_row_index':start,'end_row_index':end,'range':f'A{start+1}:F{end}'})
    return grid,plan,pages


def batches_for(pages,link):
    # Iterate one page per sheet per round. Each response has at most five sheet objects.
    page_order=sorted(pages,key=lambda p:p['start_row_index'])
    batches=[]
    for start in sorted({p['start_row_index'] for p in page_order}):
        round_pages=[p for p in page_order if p['start_row_index']==start]
        for offset in range(0,len(round_pages),5):
            group=round_pages[offset:offset+5]
            ranges=["'"+p['sheet_name'].replace("'","''")+"'!"+p['range'] for p in group]
            args={'spreadsheet_id':BINDING['spreadsheet_id'],'link_id':link,'cell_fields':'effectiveValue','ranges':ranges}
            batches.append(({'index':len(batches),'tool':CELLS,'arguments':args},group))
    return batches


def cell_value(cell):
    require(isinstance(cell,dict),'A célula está incompleta.')
    if not cell:
        return ''
    value=cell.get('effectiveValue')
    require(isinstance(value,dict) and len(value)==1,'A célula não trouxe o valor efetivo.')
    kind,scalar=next(iter(value.items()))
    if kind=='stringValue' and isinstance(scalar,str):
        return scalar
    if kind=='boolValue' and type(scalar) is bool:
        return scalar
    if kind=='numberValue' and type(scalar) in {float,int} and math.isfinite(scalar):
        return int(scalar) if type(scalar) is float and scalar.is_integer() else scalar
    raise ValueError('Célula contém erro de fórmula ou valor efetivo incompatível.')


def unpack_batch(response,group,grid):
    expected={page['sheet_name']:page for page in group}
    result={}
    for item in response.get('sheets',[]):
        properties=item['properties']
        name=properties['title']
        require(name in expected and name not in result,'Aba inesperada ou duplicada na resposta de células.')
        sheet_id,total_rows,columns=grid[name]
        require(properties['sheetId']==sheet_id and (properties['gridProperties']['rowCount'],properties['gridProperties']['columnCount'])==(total_rows,columns),
                'A aba mudou durante a consulta: '+name)
        page=expected[name]
        blocks=item.get('data')
        require(isinstance(blocks,list) and len(blocks)==1,'Intervalo ausente ou repetido em '+name)
        data=blocks[0]
        require(data.get('startRow',0)==page['start_row_index'] and data.get('startColumn',0)==0,
                'Coordenadas de retorno divergentes em '+name)
        native_rows=data.get('rowData',[])
        require(isinstance(native_rows,list) and len(native_rows)<=page['end_row_index']-page['start_row_index'],
                'A resposta ultrapassou as linhas solicitadas.')
        width=6 if name==INBOX else len(SCHEMA['tables'][name]['columns'])
        rows=[]
        for native in native_rows:
            values=native.get('values',[])
            require(isinstance(values,list) and len(values)<=width,'A resposta ultrapassou as colunas solicitadas.')
            rows.append([cell_value(v) for v in values])
        result[name]=rows
    require(set(result)==set(expected),'Um lote chegou incompleto.')
    return result


def dispatch(action,spec):
    require(action in {'desk-read-plan','desk-read-copy'},'Comando de leitura desconhecido.')
    grid,plan,pages=plan_parts(spec)
    before=spec['before']
    link=before['link_id']
    calls=batches_for(pages,link)
    if action=='desk-read-plan':
        return {'kind':'NATIVE_CONNECTOR_READ_PLAN','batches':[c for c,_ in calls],'after_request':{
            'tool':METADATA,'arguments':{'link_id':link,'spreadsheet_id':BINDING['spreadsheet_id']}},
            'page_rows':spec.get('page_rows',1000),'remote_read_performed_by_cli':False}
    after=spec['after']
    end=check_envelope(after,METADATA,link)
    start=timestamp(before['observed_at'])
    require(start<end and metadata_grid(after['response'])==grid,
            'As duas leituras de metadados divergem ou estão fora de ordem. Releia a planilha.')
    require(before.get('drive_version')==after.get('drive_version'),
            'A versão do arquivo mudou durante a consulta. Releia os lotes.')
    evidence=spec['batches']
    require(isinstance(evidence,list) and len(evidence)==len(calls),'Número incorreto de lotes.')
    captured={}
    for batch in evidence:
        number=batch.get('index')
        require(type(number) is int and 0<=number<len(calls) and number not in captured,'Índice de lote ausente, repetido ou inválido.')
        captured[number]=batch
    by_page={}
    for call,group in calls:
        batch=captured[call['index']]
        observed=check_envelope(batch,CELLS,link)
        require(start<=observed<=end and batch.get('ranges')==call['arguments']['ranges'],
                'Origem, horário ou intervalos do lote divergiram do plano.')
        fields=batch.get('cell_fields','effectiveValue')
        require(fields=='effectiveValue','Solicite somente effectiveValue na leitura.')
        unpacked=unpack_batch(batch['response'],group,grid)
        for page in group:
            by_page[page['sheet_name'],page['start_row_index']]=unpacked[page['sheet_name']]
    values=[by_page[p['sheet_name'],p['start_row_index']] for p in plan['pages']]
    snapshot=reconstruct(plan,values,spec.get('scope',{}),after['observed_at'])
    # Absolute positions in a sparse inbox remain stable, including gaps between pages.
    intake=[]
    for page in (p for p in pages if p['sheet_name']==INBOX):
        rows=by_page[INBOX,page['start_row_index']]
        if rows:
            intake.extend([[] for _ in range(page['start_row_index']-len(intake))])
            intake.extend(rows)
    require(intake and intake[0]==HEADERS,'Cabeçalho da fila incompatível.')
    require(all(all(isinstance(cell,str) for cell in row) for row in intake),
            'A fila de direção contém um campo não textual. Confira a linha no Google Sheets.')
    snapshot=attach_intake(snapshot,intake)
    snapshot['intake_values']=intake
    snapshot['read_provenance']={'account':before['account'],'link_id':link,'spreadsheet_id':BINDING['spreadsheet_id'],
        'first_metadata_at':before['observed_at'],'last_metadata_at':after['observed_at'],'grid_sha256':fingerprint(grid),
        'batches':len(calls),'effective_values':True,'drive_version':after.get('drive_version'),
        'atomic':False,'remote_read_performed_by_cli':False}
    return snapshot
