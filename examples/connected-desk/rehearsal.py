"""Prepare an isolated two-episode rehearsal. No remote writes."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from episode_workflow import initialize_episode
from shared_state import SCHEMA,canonical,prepare,index
from shot_workflow import ref,link_change,digest_file
from series_bible import TOPIC
PROJECT='TEST-CPE13';EP1=PROJECT+'-EP1';EP2=PROJECT+'-EP2'
NAME='A última água · ensaio de direção'
ACTOR='CPE 1.3 · ensaio identificado'
MESSAGE='Pedido de implementação e verificação do Studio 1.3; registros sintéticos de ensaio, sem preferência pessoal.'
SYSTEM={'id','revision','updated_by','updated_at','last_op_id'}
def auth(op,at):
    return {'actor':ACTOR,'authorized':True,'user_message_ref':MESSAGE,'op_id':op,'at':at}
def raw_change(c):
    return {'table':c['table'],'id':c['id'],'expected_revision':None,'values':{k:v for k,v in c['after'].items() if k not in SYSTEM}}
def seed(s,at,op='CPE13-REHEARSAL-SETUP-01'):
    a=auth(op,at)
    e1=initialize_episode(s,{'project_id':PROJECT,'project_name':NAME,'episode_title':'A chegada','target_seconds':60,'genre':'drama','is_test':True},a)
    e2=initialize_episode(e1['candidate'],{'project_id':PROJECT,'episode_title':'A volta à estação','target_seconds':60,'new_episode':True,'include_test':True},a)
    ch=[raw_change(c) for c in [*e1['changes'],*e2['changes']]]
    def add(table,key,ep,**vals):
        ch.append({'table':table,'id':key,'expected_revision':None,'values':{'project_id':PROJECT,'episode_id':ep,'is_test':True,**vals}})
    cases=[('D1',EP1,'character_knowledge','DAVI','chegada','identidade desconhecida',10,'SH01',''),
           ('D2',EP1,'audience_knowledge','AUDIENCE','chegada','Rosa está na estação',12,'SH01',''),
           ('D3',EP1,'location','ESTAÇÃO','porta','W1 a oeste',13,'SH01',''),
           ('D4',EP2,'character_knowledge','DAVI','chegada','é Rosa',68,'SH06','TEST-CPE13-D1')]
    for key,ep,kind,subject,field,value,seq,beat,prior in cases:
        fact={'kind':kind,'subject':subject,'key':field,'value':value,'sequence':seq,'beat':beat}
        if prior:fact['previous_decision_id']=prior
        add('Decisions',PROJECT+'-'+key,ep,gate_id='G3',topic=TOPIC,choice=canonical(fact),rationale='Decisão narrativa do ensaio: '+value,user_message_ref=MESSAGE,status='RECORDED')
    add('Screenplays',PROJECT+'-ROTEIRO',EP2,gate_id='G4',version='1',title='A volta à estação',text_or_ref='ESTAÇÃO · DIA\nDavi entrega o cantil. Lia troca de mão e bebe.\nDAVI: Quem chegou?\nDepois da buzina, ele vê Rosa à porta.',status='DRAFT')
    specs=json.loads((R/'examples/series-worked/last-water-shots.json').read_text(encoding='utf-8'))
    for shot in specs:
        key=shot['key']
        add('Shot List',PROJECT+'-'+key,EP2,gate_id='G10',version='ensaio-v1',scene_beat='Estação',order=shot['order'],duration_s=shot['duration'],purpose=shot['purpose'],action=shot['action'],camera_blocking=shot['camera'],sound_edit=shot['sound'],start_end_state=canonical({'in':{'cantil':shot['entry'],'tampa':shot['cap_in']},'out':{'cantil':shot['exit'],'tampa':shot['cap_out']}}),status='DRAFT')
        uri=f"examples/series-worked/frames/P{shot['order']:02d}.png"
        add('Artifact Registry',PROJECT+'-REF-'+key,EP2,gate_id='G10',kind='REFERENCE',department='composition',version=1,uri=uri,sha256=digest_file(R/uri),origin='Quadro esquemático autoral do ensaio da estação.',rights='Autoral, uso didático autorizado',status='DRAFT')
    for suffix,uri in [('CORTE-ORIGINAL','examples/series-worked/SH06-previs.mp4'),('CORTE-ADIANTADO','examples/connected-desk/SH06-som-antecipado.mp4')]:
        add('Artifact Registry',PROJECT+'-'+suffix,EP2,gate_id='G12',kind='NARRATIVE_PREVIS',department='editing',version=1,uri=uri,sha256=digest_file(R/uri),origin='Prévia esquemática · '+suffix,rights='Autoral, uso didático autorizado',status='REVIEW_REQUIRED')
    candidate=prepare(s,{**a,'changes':ch})['candidate'];ix=index(candidate)
    def link(kind,src,dst,key,**extra):
        ch.append(link_change(candidate,{'relation':kind,'decision_id':PROJECT+'-L-'+key,'reason':'Vínculo de produção do ensaio sintético.','authorization':a,**extra},ref(src[0],ix[src[0]][src[1]]),ref(dst[0],ix[dst[0]][dst[1]])))
    for shot in specs:
        key=shot['key']
        link('reference',('Artifact Registry',PROJECT+'-REF-'+key),('Shot List',PROJECT+'-'+key),key,role='image_references')
    for suffix in ['CORTE-ORIGINAL','CORTE-ADIANTADO']:
        link('take',('Shot List',PROJECT+'-SH06'),('Artifact Registry',PROJECT+'-'+suffix),suffix)
    link('uses',('Shot List',PROJECT+'-SH05'),('Shot List',PROJECT+'-SH06'),'CANTIL',field='cantil')
    return prepare(s,{**a,'changes':ch})

