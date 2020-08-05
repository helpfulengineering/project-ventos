import yaml, os, re, glob, math, numbers
import pandas as pd
from collections import namedtuple

dictionary_path = 'datadictionary'

# special loader with duplicate key checking
class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            assert key not in mapping
            mapping.append(key)
        return super().construct_mapping(node, deep)

def yaml_file(name):
    return os.path.join(dictionary_path, f'{name}.yaml')

# compare the fields i an item to a list to see if we have
# interchangeable fields
def must_have_n_of(item, fields, n = 1):
    return f'must have {n} of {fields} found {list(item.keys())}' \
        if len(fields - item.keys()) != len(fields)-n else False

# compare the fields i an item to a list to see if we have
# interchangeable fields
def foreign_key(key, foreign, data):
    return f'key {key} not found in {foreign}' \
            if key not in data[foreign].keys() else False

# trim off the last word in the key, converting an alarm id to
# a state key
def alarm_to_state(key):
    return key.rsplit('_', 1)[0]

def isNumber(i):
    return isinstance(i, numbers.Number)and not math.isnan(i)

def pretty_values(r):
    return ("" if pd.isnull(r.default)
               else f"{r.default:.{r.significant_digits}f} " if isNumber(r.default)
               else f"{r.default} "
           ) + (
            f"({', '.join(r.enum)}) " if type(r.enum)==list
            else ('' if r.units in ['time', 'Boolean']
                else f"({r.min:.{r.significant_digits}f}-{r.max:.{r.significant_digits}f} "
                f'step {r.resolution:g}) '
                )
            + f"{r.units}")

allowed_c_types = ['bool', 'enum', 'byte', 'int', 'unsigned int', 'long', 'unsigned long']

def c_type(r):
    if type(r) == dict: # this is a horrible hack
        r = namedtuple('x', r.keys())(*r.values())
    if r.sot == 'timestamp':
        return 'unsigned long'
    elif hasattr(r, 'enum') and type(r.enum)==list:
        return 'enum'
    if r.units == 'Boolean':
        return 'bool'
    elif isNumber(r.resolution):
        max_value = r.max/r.resolution
        min_value = r.min/r.resolution
        signed = min_value < 0
        size = max(max_value, abs(min_value)) * (2 if signed else 1)
        assert size <= 4294967295
        base = 'long' if size > 65535 else 'int' if size > 255 or signed else 'byte'
        return f"{'' if signed else 'unsigned ' if base != 'byte' else ''}{base}"
    else:
        return 'error'


meta_meta = {
    'state': {
        'required': {
            'notes': { },
            'status': { 'enum': ['core', 'draft', 'proposed'] },
            'sot': {'enum': ['config', 'operator', 'sensor', 'derived', 'timestamp']},
            },
        'optional': {
            'units': {
                'enum': ['miliseconds', 'seconds', 'time', 'BPM',
                    'cmH2O', 'mBar', 'mmHg',
                    'ml', 'kg', 'cm', 'percent', 'ml/minute',
                    'Volts', 'Celsius',
                    'Boolean', 'kilobytes'],},
            'enum': {
                'type': [list]},
            'min': {
                'type': [int, float]},
            'max': {
                'type': [int, float]},
            'default': {},
            'resolution': {
                'type': [int, float]},
            },
        'extra_checks': [
            # must have either unit or enum, but not both
            lambda k,i,m,d: must_have_n_of(i, ['units', 'enum']),
            # config and operator variables must have a default
            lambda k,i,m,d: must_have_n_of(i, ['default'], n=1) if i['sot'] in ['config', 'operator'] else False,
            # must have resolution, min and max, if not enum, Bool or time units
            lambda k,i,m,d: must_have_n_of(i, ['max', 'min', 'resolution'], n=3) if
               i.get('units', 'enum') not in ['Boolean', 'time', 'enum'] else False,
            # enum, Bool and time must not have min, max, or resolution
            lambda k,i,m,d: must_have_n_of(i, ['max', 'min', 'resolution'], n=0) if
               i.get('units', 'enum') in ['Boolean', 'time', 'enum'] else False,
            # enum must not have min, max
            lambda k,i,m,d: must_have_n_of(i, ['units'], n=0) if type(i.get('enum', None)) == list else False,
            # min must be less than max if present
            lambda k,i,m,d: f"min {i.get('min', False)} is not less than max {i.get('max', False)}" if
                    (not isinstance(i.get('min', False), bool)) and (i.get('min', -math.inf) >= i.get('max', math.inf)) else False,
            # default must between min and max if numeric
            lambda k,i,m,d: f"default {i['default']} not between {i['min']} and {i['max']}" if
                (isinstance(i.get('default', False), numbers.Number) and
                not (i.get('min', -math.inf) <= i.get('default', False) <= i.get('max', math.inf)))
                else False,
            # must have valid c type
            lambda k,i,m,d: f"invalid C type {c_type(i)}" if
                c_type(i) not in allowed_c_types else False,
            ],
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
        'optional': {
            'min': {
                'type': [int, float]},
            'max': {
                'type': [int, float]},
            'default': {
                'type': [int, float]},
            },
        'extra_checks': [
            # stripping the last underscore work (eg "_hi") must find a state value
            lambda k,i,m,d: foreign_key(alarm_to_state(k), 'state', d),
            # default must be between min and max
            lambda k,i,m,d: f"default {i['default']} not between {i['min']} and {i['max']}"
               if not (i['min'] <= i['default'] <= i['max']) else False,
            ],
        #
        'key_regex': '^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*(_(HI|LOW|DIV|DIFF))$',
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
    'mode': {
        'required': {'full': {},
                 },
        'optional': {
            'notes': {},
                 },
        'key_regex': '^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$',
        },
    'capability': {
        'required': {
            'status': {
                'enum': ['possible', 'optional', 'desirable', 'required']
                }
                 },
        'optional': {
            'notes': {},
                 },
        'key_regex': '^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$',
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

# load the entire metadata into memory and return
def load_yaml():
    data = {}
    for f, meta in meta_meta.items(): # loop over files
        yaml_text = open(yaml_file(f), 'r')
        data[f] = yaml.load(yaml_text, Loader=UniqueKeyLoader)
    return data

