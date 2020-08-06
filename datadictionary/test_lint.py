import yaml, os, re, glob
import pytest
import ventos_yaml as vy
log = print

def test_all_files_have_meta():
    base = lambda f: os.path.splitext(os.path.basename(f))[0]
    dictionary_yaml_glob = glob.glob(vy.yaml_file(vy.dictionary_path, '*'))
    files = [base(f) for f in dictionary_yaml_glob]
    assert set(files) == set(vy.meta_meta.keys())

def test_lint():
    data = vy.load_yaml()
    # generic linting
    error = {}
    def log_error(key_list, err):
        key = '-'.join(key_list)
        error[key] = error.get(key, [])
        error[key].append(err)
    for f, meta in vy.meta_meta.items(): # loop over files
        required = meta['required']
        allowed = {**required, **meta['optional']}
        key_pattern = re.compile(meta['key_regex'])
        for key, fields in data[f].items(): # loop over items
            extra = fields.keys() - allowed.keys()
            missing = required.keys() - fields.keys()
            if len(missing) + len(extra):
                if len(missing):
                    log_error([f, key], f'missing: {missing}')
                if len(extra):
                    log_error([f, key], f'extra: {extra}')
            if not key_pattern.match(key):
                log_error([f, key],
                    f"#### key: {key} does not match {meta['key_regex']}")
            for field, val in fields.items():
                field_meta = allowed.get(field, {})
                enum = field_meta.get('enum', False)
                if enum and val not in enum:
                    log_error([f, key, field],
                    f'#### unknown value: "{val}" expecting one of {enum}')
                field_type = field_meta.get('type', False)
                if field_type and type(val) not in field_type:
                    log_error([f, key, field],
                    f'#### bad type: "{val}" got {type(val)} expecting {field_type}')
            for extra_check in meta.get('extra_checks', []):
                extra_error = extra_check(key, fields, meta, data)
                if extra_error:
                    log_error([f, key], f'#### "{extra_error}"')
    assert error == {}

# Note this test does not include writing the files or verifying file timestamps or size etc
def test_package():
    import package

    package.main({'sourcedir': vy.dictionary_path, 'job': ['All']})
