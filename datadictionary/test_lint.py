#!/usr/bin/python3.7
import yaml, os, re, glob
import pytest
dictionary_path = 'datadictionary'
verbose = True or False
log = print
def noop(x):
    pass
log = print if verbose else noop

meta_meta = {
        'alarm': {
            'required': ['notes', 'status', 'source'],
            'optional': [],
            'key_regex': '^[A-Z0-9]+(_[A-Z0-9]+)*(_(HI|LOW|DIV|DIFF))$',
            },
        'alarm_level': {
            'required': ['notes', 'synonyms', 'status'],
            'optional': [],
            'key_regex': '^[A-Z]+$',
            },
        'abbreviation': {
            'required': ['full', 'source'],
            'optional': ['definition', ],
            'key_regex': '^[a-zA-Z0-9]*$',
            },
}

def test_all_files_have_meta():
    base = lambda f: os.path.splitext(os.path.basename(f))[0]
    dictionary_yaml_glob = glob.glob(os.path.join(dictionary_path, '*.yaml'))
    files = [base(f) for f in dictionary_yaml_glob]
    assert set(files) == set(meta_meta.keys())

def test_lint():
    data = {}
    # generic linting
    total_errors = 0
    for f, meta in meta_meta.items():
        errors = 0
        required = meta['required']
        allowed = meta['required'] + meta['optional']
        key_pattern = re.compile(meta['key_regex'])
        yaml_text = open(os.path.join(dictionary_path, f'{f}.yaml'), 'r').read()
        data[f] = yaml.safe_load(yaml_text)
        log(f"### {f} {len(data[f])} rows:\n####required = {required}\n####allowed = {allowed} ")
        for key, fields in data[f].items():
            present = fields.keys()
            extra = present - allowed
            missing = required - present
            if len(missing) + len(extra):
                log(f"### {f}.{key} present: {present}")
                if len(missing):
                    errors +=1
                    log(f'missing: {missing}')
                if len(extra):
                    errors +=1
                    log(f'extra: {extra}')
            if not key_pattern.match(key):
                errors +=1
                log(f"key: {key} does not match {meta['key_regex']}")
        log(f'### {f} errors {total_errors}')
        total_errors += errors
    log(f'### {f} total errors {total_errors}')

    if (total_errors):
        raise Exception(f'Linting data dictionary: errors {total_errors}')


