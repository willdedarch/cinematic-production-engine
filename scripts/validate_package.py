#!/usr/bin/env python3
"""Validate the public package using synthetic evidence without a connected-account export."""
import ast,csv,hashlib,json,re,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'evals')]
from shared_state import verify_readback
from public_journal_fixtures import fixture_pair
from route_knowledge import route
from harness_runtime import policies
from privacy_scan import scan

def check(ok,message):
    if not ok:raise ValueError(message)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))

def main():
    files=[p for p in ROOT.rglob('*') if p.is_file() and not set(p.parts)&{'.git','__pycache__'}]
    check(not any(p.suffix in {'.pyc','.pyo'} or p.is_symlink() for p in files),'Nonportable package file')
    version=load('RELEASE-METADATA.json')['skill_version']
    front=(ROOT/'SKILL.md').read_text(encoding='utf8').split('---',2)
    check(len(front)==3 and "version: '"+version+"'" in front[1],'Skill frontmatter/version')
    check(re.search(r'^name: cinematic-production-engine$',front[1],re.M) is not None,'Skill name')
    description=re.search(r'^description: >-\n((?:^  \S[^\n]*\n)+)',front[1],re.M)
    folded=' '.join(description[1].split()) if description else ''
    check(0<len(folded)<=1024,'Skill description must be a nonempty folded YAML scalar')
    parsed={'json':0,'python':0}
    for path in files:
        if path.suffix=='.json':
            json.loads(path.read_text(encoding='utf-8-sig'));parsed['json']+=1
        elif path.suffix=='.py':
            ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path));parsed['python']+=1
        elif path.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
                if re.match(r'[a-zA-Z]+:|#',target):continue
                item=(path.parent/target.split('#')[0]).resolve()
                check(item.is_relative_to(ROOT) and item.exists(),'Broken Markdown link '+str(path.relative_to(ROOT))+' -> '+target)
    provenance=load('legacy/original-provenance.json')
    check(provenance['original_sha256']=='38582e59b870ff1bb6f261a54cdf8d01569661bbc18bf436f6c38c4a75692e8e' and not provenance['original_distributed'],'Original provenance')
    check(not (ROOT/'legacy/cinematic-production-engine-v3.zip').exists(),'Private legacy archive must not be public')
    for number in range(16):check(all(row['text'] for row in route('G'+str(number))['loaded']),'Empty reading route')
    policies()
    schema=load('schemas/shared-state.tables.json');binding=load('integrations/google-sheets.binding.json')
    check(len(schema['tables'])==35 and set(schema['tables'])==set(binding['table_ids']),'Canonical table coverage')
    check(set(schema['tables'])<=set(binding['sheet_ids']),'Missing sheet binding')
    check(binding['spreadsheet_id'].startswith('CONFIGURE_'),'Public distribution has a production binding')
    for name in ('native-test-plan','native-archive-plan','link-repair-plan'):
        plan,state=fixture_pair(name)
        check(verify_readback(plan,state,True)['status']=='CONFIRMED','Synthetic journal compatibility')
    library=load('references/visual-library.json')
    for row in library:
        path=(ROOT/row['uri']).resolve()
        check(path.is_relative_to(ROOT) and path.is_file(),'Missing visual reference')
        check(digest(path)==row['sha256'],'Changed visual reference '+row['id'])
    for pair in (ROOT/'examples/takes').glob('*-pair.json'):
        title=pair.name.split('-pair')[0];manifest=json.loads(pair.read_text(encoding='utf8'))
        check({digest(p) for p in pair.parent.glob(title+'-*.mp4')}=={r['sha256'] for r in manifest['takes'].values()},'Take bytes differ')
    with (ROOT/'audits/requirements-traceability.csv').open(encoding='utf-8-sig',newline='') as stream:requirements=list(csv.DictReader(stream))
    check(len(requirements)>=99,'Lost original requirement coverage')
    for row in requirements:
        for name in row['implementation_or_evidence'].split('; '):check((ROOT/name).exists(),'Missing requirement evidence '+name)
    board=load('examples/series-worked/storyboard.json')['cards']
    check(len(board)==6 and sum(c['duration_s'] for c in board)==60,'Sequence example changed')
    for card in board:
        pack=load('examples/series-worked/'+card['shot']['id']+'-manual.json')
        check(pack['shot']==card['shot'] and pack['execution']=='MANUAL','Manual handoff identity')
        for ref in pack['attachment_order']:check(digest(ROOT/ref['file'])==ref['sha256'],'Manual handoff reference')
    check(load('templates/library-seed.json')['tables']['Creative Preferences']==[],'Public seed must not contain a prior director preference')
    forbidden={'local-binding.json','host-setup.md','link-repair-confirmed-journal.json','visual-confirmed-journal.json','final-native-verification.json'}
    check(not any(p.name in forbidden for p in files),'Private account material in public package')
    private=scan(ROOT)
    check(private['status']=='PASS','Privacy scan '+json.dumps(private['findings'][:8]))
    manifest=load('audits/file-manifest.json');excludes={'audits/file-manifest.json','audits/package-validation.json'}
    actual={p.relative_to(ROOT).as_posix():p for p in files if p.relative_to(ROOT).as_posix() not in excludes}
    expected={row['path']:row for row in manifest['files']}
    check(set(actual)==set(expected),'Inventory differs')
    for name,path in actual.items():check(digest(path)==expected[name]['sha256'] and path.stat().st_size==expected[name]['bytes'],'Inventory bytes '+name)
    return {'status':'PASS','skill_version':version,'files':len(files),'parsed':parsed,'synthetic_journal_cases':3,
      'native_account_exports_included':False,'visual_references_hashed':len(library),'requirement_sections_checked':len(requirements),
      'gate_routes':16,'privacy':private['status'],'artistic_approval':False,'remote_read_performed':False}

if __name__=='__main__':print(json.dumps(main(),ensure_ascii=False,indent=2))
