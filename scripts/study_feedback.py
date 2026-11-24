"""Keep human study judgments private and immutable, distinct from production approvals."""
import hashlib
import json
from pathlib import Path
from shared_state import canonical,fingerprint,require

DECISIONS={'A','B','TIE','BOTH_FAIL','REJECT','REVISE','APPROVE_STUDY'}


def record_feedback(spec,workspace):
    require(spec.get('authorized') is True and spec.get('actor') and spec.get('message_ref'),
            'Bind feedback to the actual received human message')
    require(spec.get('decision') in DECISIONS and isinstance(spec.get('reason'),str),
            'A study judgment needs its observed choice and actual stated reason')
    require(isinstance(spec.get('study_id'),str) and spec['study_id'].strip(),'Study identity missing')
    materials=spec.get('materials')
    require(isinstance(materials,list) and materials,'Study materials missing')
    pins=[]
    for material in materials:
        path=Path(material['path']).resolve()
        require(path.is_file(),'Study material unavailable')
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        require(sha==material.get('sha256'),'Study material changed after presentation')
        pins.append({'id':material['id'],'path':str(path),'sha256':sha})
    row={'kind':'PRIVATE_DIRECTOR_STUDY_FEEDBACK','study_id':spec['study_id'],'actor':spec['actor'],
         'message_ref':spec['message_ref'],'decision':spec['decision'],'reason':spec['reason'],
         'materials':pins,'production_approval':False,'scope':'these exact study materials only',
         'global_preference':False}
    key=fingerprint([row['study_id'],row['message_ref']])
    target=Path(workspace).resolve()/'director-studies'/(key+'.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        with target.open('x',encoding='utf8') as stream:stream.write(canonical(row)+'\n')
    except FileExistsError:
        require(json.loads(target.read_text(encoding='utf8'))==row,'Feedback identity already used for different content')
    return {'kind':'PRIVATE_LOCAL_STUDY_RECORDED','file':str(target),'remote_write':False,
            'production_approval':False,'global_preference':False}


def comparison_metrics(agent_choices,human_choice):
    require(human_choice in {'A','B','TIE','BOTH_FAIL'},'Pairwise human label missing')
    require(isinstance(agent_choices,list) and agent_choices and
            all(choice in {'A','B','TIE','BOTH_FAIL'} for choice in agent_choices),'Pairwise agent labels missing')
    return {'material_pair_n':1,'human_judgment_n':1,'agent_comparisons':len(agent_choices),
            'pairwise_agreement':sum(choice==human_choice for choice in agent_choices)/len(agent_choices),
            'artistic_approval_rate':None,'generalization_measured':False}
