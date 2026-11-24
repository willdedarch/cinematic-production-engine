"""Resolve a private local override without embedding an account in the public package."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_binding(root=ROOT):
    root=Path(root)
    local=root/'integrations/local-binding.json'
    source=local if local.is_file() else root/'integrations/google-sheets.binding.json'
    binding=json.loads(source.read_text(encoding='utf-8-sig'))
    required={'schema_version','account','link_id','spreadsheet_id','spreadsheet_url','sheet_ids','table_ids'}
    if not isinstance(binding,dict) or not required<=set(binding):
        raise ValueError('Incomplete Google Sheets binding')
    if binding['schema_version']!='3.1.0':
        raise ValueError('Unsupported binding schema')
    if not isinstance(binding['spreadsheet_id'],str) or not re.fullmatch(r'[A-Za-z0-9_-]+',binding['spreadsheet_id']):
        raise ValueError('Use the raw spreadsheet identity')
    # Links must follow the same identity used by metadata/readback guards after an account migration.
    binding['spreadsheet_url']='https://docs.google.com/spreadsheets/d/'+binding['spreadsheet_id']+'/edit'
    return binding
