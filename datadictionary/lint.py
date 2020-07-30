#!/usr/bin/python3.7
import yaml, os
path = 'datadictionary'
verbose = False
log = print
def noop(x):
    pass
log = print if verbose else noop

meta_meta = {
        'alarms': {
            'required': ['notes', 'source', 'status'],
            'optional': []
            },
        'abbreviations': {
            'required': ['full', 'source'],
            'optional': ['definition', ]
            },
}
data = {}

# generic linting
total_errors = 0
for f, meta in meta_meta.items():
    errors = 0
    required = meta['required']
    allowed = meta['required'] + meta['optional']
    yaml_text = open(os.path.join(path, f'{f}.yaml'), 'r').read()
    data[f] = yaml.load(yaml_text)
    log(f"### {f} {len(data[f])} rows:\n####required = {required}\n####allowed = {allowed} ")
    for key, fields in data[f].items():
        present = fields.keys()
        extra = [f for f in present if f not in allowed]
        missing = [f for f in required if f not in present]
        if len(missing) + len(extra):
            log(f"### {f}.{key} present: {present}")
            if len(missing):
                errors +=1
                log(f'missing: {missing}')
            if len(extra):
                errors +=1
                log(f'extra: {extra}')
    log(f'### {f} errors {total_errors}')
    total_errors += errors
log(f'### {f} total errors {total_errors}')

if (total_errors):
    raise Exception(f'Linting data dictionary: errors {total_errors}')


