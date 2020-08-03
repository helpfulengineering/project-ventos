import yaml, os, re, glob
import pytest
import ventos_yaml as vy
log = print

def test_all_files_have_meta():
    base = lambda f: os.path.splitext(os.path.basename(f))[0]
    dictionary_yaml_glob = glob.glob(vy.yaml_file('*'))
    files = [base(f) for f in dictionary_yaml_glob]
    assert set(files) == set(vy.meta_meta.keys())

def test_lint():
    data = vy.load_yaml()
    # generic linting
    total_errors = 0
    for f, meta in vy.meta_meta.items(): # loop over files
        errors = 0
        required = meta['required']
        allowed = {**required, **meta['optional']}
        key_pattern = re.compile(meta['key_regex'])
        for key, fields in data[f].items(): # loop over items
            extra = fields.keys() - allowed.keys()
            missing = required.keys() - fields.keys()
            if len(missing) + len(extra):
                if len(missing):
                    errors +=1
                    log(f'missing: {missing}')
                if len(extra):
                    errors +=1
                    log(f'extra: {extra}')
            if not key_pattern.match(key):
                errors +=1
                log(f"#### key: {key} does not match {meta['key_regex']}")
            for field, val in fields.items():
                field_meta = allowed.get(field, {})
                enum = field_meta.get('enum', False)
                if enum and val not in enum:
                    log(f'#### unknown "{field}" value: "{val}" expecting one of {enum}')
                    errors +=1
            for extra_check in meta.get('extra_checks', []):
                extra_errors = extra_check(key, fields, meta, data)
                if extra_errors:
                    log(f'#### {key} -"{extra_errors}"')
                    errors +=1

        total_errors += errors
        log(f'### {f} errors {errors}')
    log(f'### total errors {total_errors}')

    assert total_errors == 0


def test_package():
    import package
    package.main()
