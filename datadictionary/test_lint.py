#!/usr/bin/python3.7
import yaml, os, re, glob
import pytest
dictionary_path = 'datadictionary'

log = print
from yaml import Loader

from yaml.constructor import ConstructorError

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class UniqueKeyLoader(Loader):
    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.nodes.MappingNode):
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError:
                raise ConstructorError(
                       f"while constructing a mapping", node.start_mark,
                       f"found unacceptable key ({key}) {key_node.start_mark}")
            # check for duplicate keys
            if key in mapping:
                raise ConstructorError(
                  f"duplicate key [{key}] line: {key_node.start_mark.line}")
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

def test_frish():
    assert True

# compare the fields i an item to a list to see if we have
# interchangeable fields
def must_have_n_of(item, fields, n = 1):
    return f'must have {n} of {fields} found {list(item.keys())}' \
        if len(fields - item.keys()) != len(fields)-n else False


meta_meta = {
    'state': {
        'required': {
            'notes': { },
            'status': { 'enum': ['core', 'draft', 'proposed'] },
            'sot': {'enum': ['config', 'operator', 'sensor', 'derived', 'timestamp']},
            },
        'optional': {
            'units': {},
            'enum': {},
            'min': {},
            'max': {},
            'default': {},
            },
        'extra_checks': (lambda i: must_have_n_of(i, ['units', 'enum'])),
        'key_regex': '^[A-Z]+([A-Z0-9])*(_[A-Z0-9]+)*$',
        },
    'alarm': {
        'required': {
            'notes': { },
            'status': {
                'enum': ['core', 'proposed']
                },
            'source': {
                }},
        'optional': {},
        'key_regex': '^[A-Z0-9]+(_[A-Z0-9]+)*(_(HI|LOW|DIV|DIFF))$',
        },
    'alarm_level': {
        'required': {
             'notes': {},
             'synonyms': {},
             'status': {
                'enum': ['core', 'proposed'],
                 }},
        'optional': {},
        'key_regex': '^[A-Z]+$',
        },
    'abbreviation': {
        'required': {'full': {},
                 'source': {},
                 },
        'optional': {'definition': {},
                 },
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
    for f, meta in meta_meta.items(): # loop over files
        errors = 0
        required = meta['required']
        allowed = {**required, **meta['optional']}
        key_pattern = re.compile(meta['key_regex'])
        yaml_text = open(os.path.join(dictionary_path, f'{f}.yaml'), 'r').read()
        data[f] = yaml.load(yaml_text, Loader=UniqueKeyLoader)
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
            extra_checks = meta.get('extra_checks', False)
            if extra_checks:
                extra_errors = extra_checks(fields)
                if extra_errors:
                    log(f'#### {key} -"{extra_errors}"')
                    errors +=1

        total_errors += errors
        log(f'### {f} errors {errors}')
    log(f'### total errors {total_errors}')

    assert total_errors == 0


