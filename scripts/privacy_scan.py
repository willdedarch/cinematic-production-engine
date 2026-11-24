"""Detect environment-specific identifiers in a public release, including nested archives."""
import argparse
import codecs
import io
import json
from pathlib import Path
import re
import zipfile

RULES={
 'absolute_user_path':re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+[^\s"<>]{2,}',re.I),
 'account_link':re.compile(rb'link_[a-z0-9]{20,}',re.I),
 'private_sheet_url':re.compile(rb'docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]{25,})'),
 'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 'provider_token':re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|AIza[A-Za-z0-9_-]{30,})')
}
ARCHIVE_SUFFIXES={'.zip','.xlsx','.xlsm','.docx','.pptx','.odt','.ods','.epub','.whl'}
TEXT_SUFFIXES={'.txt','.md','.csv','.tsv','.json','.xml','.html','.yaml','.yml','.log','.ini','.toml','.rels'}


def text_payload(name,data):
    for markers, encoding in (((codecs.BOM_UTF32_LE,codecs.BOM_UTF32_BE),'utf-32'),
                              ((codecs.BOM_UTF16_LE,codecs.BOM_UTF16_BE),'utf-16')):
        if data.startswith(markers):
            return data.decode(encoding,errors='replace').encode('utf-8')
    sample=data[:512]
    likely_wide=sample.count(b'\0') > len(sample)//4 or (Path(name).suffix.lower() in TEXT_SUFFIXES and b'\0' in data)
    if sample and not sample.startswith(b'PK') and likely_wide:
        for encoding in ('utf-16-le','utf-16-be'):
            candidate=data.decode(encoding,errors='replace').encode('utf-8')
            if any(pattern.search(candidate) for pattern in RULES.values()):
                return candidate
    return data


def inspect_bytes(name,data,depth=0):
    findings=[]
    payload=text_payload(name,data)
    for rule,pattern in RULES.items():
        for match in pattern.finditer(payload):
            if rule=='private_sheet_url' and match.group(1).startswith(b'CONFIGURE_'):
                continue
            findings.append({'file':name,'rule':rule,'offset':match.start(),
                             'offset_basis':'raw_bytes' if payload is data else 'decoded_utf8'})
    if Path(name).suffix.lower() in ARCHIVE_SUFFIXES or data.startswith(b'PK\x03\x04'):
        if depth>=3:
            findings.append({'file':name,'rule':'archive_depth_not_inspected'})
        else:
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    expanded=sum(item.file_size for item in archive.infolist())
                    if expanded>100*1024*1024:
                        findings.append({'file':name,'rule':'archive_requires_separate_inspection'})
                    else:
                        for item in archive.infolist():
                            if not item.is_dir():
                                findings.extend(inspect_bytes(name+'!'+item.filename,archive.read(item),depth+1))
            except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError):
                findings.append({'file':name,'rule':'archive_unreadable'})
    return findings


def scan(root):
    root=Path(root).resolve()
    findings=[]
    files=0
    for path in root.rglob('*'):
        if not path.is_file() or set(path.parts)&{'.git','__pycache__'} or path.suffix in {'.pyc','.pyo'}:
            continue
        files+=1
        findings.extend(inspect_bytes(path.relative_to(root).as_posix(),path.read_bytes()))
    return {'status':'PASS' if not findings else 'REVIEW_REQUIRED','files_scanned':files,'findings':findings,
            'scope':'Known account, path and credential patterns; manual review is still required',
            'git_history_inspected':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    result=scan(args.root)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
