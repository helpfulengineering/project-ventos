""" Tests for the YAML library """
import os
import re
import glob
import ventos_yaml as vy
import package


def test_all_files_have_meta():
    """Check the YAML file list exactly matches the metadata"""
    def base(fname):
        return os.path.splitext(os.path.basename(fname))[0]

    dictionary_yaml_glob = glob.glob(vy.yaml_file(vy.DICTIONARY_PATH, '*'))
    files = [base(fname) for fname in dictionary_yaml_glob]
    assert set(files) == set(vy.META_ITEMS.keys())


def test_lint():
    """Lint all YAML files according to the meta-meta-data from `ventos_yaml`"""
    data = vy.load_yaml()
    # generic linting
    error = {}

    def log_error(key_list, err):
        key = '-'.join(key_list)
        error[key] = error.get(key, [])
        error[key].append(err)
    def check_fields(chapter, key, fields, allowed):
        for field, val in fields.items():
            field_meta = allowed.get(field, {})
            enum = field_meta.get('enum', False)
            if enum and val not in enum:
                log_error(
                    [chapter, key, field],
                    f'#### unknown value: "{val}" expecting one of {enum}')
            field_type = field_meta.get('type', False)
            if field_type and not isinstance(val, tuple(field_type)):
                log_error([
                    chapter, key, field
                ], f'#### bad type: "{val}" got {type(val)} expecting {field_type}'
                          )

    for chapter, meta in vy.META_ITEMS.items():  # loop over files
        required = meta['required']
        allowed = {**required, **meta['optional']}
        key_pattern = re.compile(meta['key_regex'])
        for key, fields in data[chapter].items():  # loop over items
            extra = fields.keys() - allowed.keys()
            missing = required.keys() - fields.keys()
            if len(missing) + len(extra) > 0:
                if len(missing) > 0:
                    log_error([chapter, key], f'missing: {missing}')
                if len(extra) > 0:
                    log_error([chapter, key], f'extra: {extra}')
            if not key_pattern.match(key):
                log_error(
                    [chapter, key],
                    f"#### key: {key} does not match {meta['key_regex']}")
            check_fields(chapter, key, fields, allowed)
            for extra_check in meta.get('extra_checks', []):
                extra_error = extra_check(key, fields, meta, data)
                if extra_error:
                    log_error([chapter, key], f'#### "{extra_error}"')
    assert error == {}


def test_package():
    """
    Note this test does not include writing the files or verifying file
    timestamps or size etc
    """
    package.main({'sourcedir': vy.DICTIONARY_PATH, 'job': ['All']})
