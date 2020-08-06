"""
Generic code for handling YAML
"""
import os
import math
import numbers
from collections import namedtuple
import pandas as pd
import yaml

DICTIONARY_PATH = 'datadictionary'


class UniqueKeyLoader(yaml.SafeLoader): # pylint: disable=too-many-ancestors
    """ YAML loader with duplicate key checking """
    def construct_mapping(self, node, deep=False):
        mapping = []
        for item in node.value:
            key = self.construct_object(item[0], deep=deep)
            assert key not in mapping
            mapping.append(key)
        return super().construct_mapping(node, deep)


def yaml_file(path, name):
    """Create a full path name for a yaml file."""
    return os.path.join(path, f'{name}.yaml')


def must_have_n_of(item, fields, num=1):
    """
    compare the fields i an item to a list to see if we have
    interchangeable fields
    """
    return f'must have {num} of {fields} found {list(item.keys())}' \
        if len(fields - item.keys()) != len(fields)-num else False


def foreign_key(key, foreign, data):
    """
     compare the fields i an item to a list to see if we have
     interchangeable fields
    """
    return f'key {key} not found in {foreign}' \
        if key not in data[foreign].keys() else False


def alarm_to_state(key):
    """
     trim off the last word in the key, converting an alarm id to
     a state key
    """
    return key.rsplit('_', 1)[0]


def is_number(i):
    """
     Test to see if a value is numeric
    """
    return isinstance(i, numbers.Number) and not math.isnan(i)


def pretty_values(rec):
    """
    Make a nice string to summarise default, range, units etc
    """
    return (
        ""
        if pd.isnull(rec.default) else f"{rec.default:.{rec.significant_digits}f} "
        if is_number(rec.default) else f"{rec.default} "
    ) + (
        f"({', '.join(rec.enum)}) " if isinstance(rec.enum, list) else
        ('' if rec.units in ['time', 'Boolean'] else
         f"({rec.min:.{rec.significant_digits}f}-{rec.max:.{rec.significant_digits}f} "
         f'step {rec.resolution:g}) ') + f"{rec.units}")


ALLOWED_C_TYPES = [
    'void', 'bool', 'enum', 'byte', 'int', 'unsigned int', 'long',
    'unsigned long'
]


def c_type(rec):
    """
    Return the C type of a variable based on its type
    """
    if isinstance(rec, dict):  # this is a horrible hack
        rec = namedtuple('x', rec.keys())(*rec.values())
    if rec.sot == 'timestamp':
        return 'unsigned long'
    if hasattr(rec, 'enum') and isinstance(rec.enum, list):
        return 'enum'
    if rec.units == 'Boolean':
        return 'bool'
    if is_number(rec.resolution):
        max_value = rec.max / rec.resolution
        min_value = rec.min / rec.resolution
        signed = min_value < 0
        size = max(max_value, abs(min_value)) * (2 if signed else 1)
        assert size <= 4294967295
        base = 'long' if size > 65535 else 'int' if size > 255 or signed else 'byte'
        return f"{'' if signed else 'unsigned ' if base != 'byte' else ''}{base}"
    return 'error'


META_ITEMS = {
    'state': {
        'required': {
            'notes': {},
            'status': {
                'enum': ['core', 'draft', 'proposed']
            },
            'sot': {
                'enum':
                ['config', 'operator', 'sensor', 'derived', 'timestamp']
            },
        },
        'optional': {
            'units': {
                'enum': [
                    'miliseconds', 'seconds', 'time', 'BPM', 'cmH2O', 'mBar',
                    'mmHg', 'ml', 'kg', 'cm', 'percent', 'ml/minute', 'Volts',
                    'Celsius', 'Boolean', 'kilobytes'
                ],
            },
            'enum': {
                'type': [list]
            },
            'min': {
                'type': [int, float]
            },
            'max': {
                'type': [int, float]
            },
            'default': {},
            'resolution': {
                'type': [int, float]
            },
        },
        'extra_checks': [
            # must have either unit or enum, but not both
            lambda k, i, m, d: must_have_n_of(i, ['units', 'enum']),
            # config and operator variables must have a default
            lambda k, i, m, d: must_have_n_of(i, ['default'], num=1)
            if i['sot'] in ['config', 'operator'] else False,
            # must have resolution, min and max, if not enum, Bool or time units
            lambda k, i, m, d: must_have_n_of(i, ['max', 'min', 'resolution'],
                                              num=3) if i.get('units', 'enum')
            not in ['Boolean', 'time', 'enum'] else False,
            # enum, Bool and time must not have min, max, or resolution
            lambda k, i, m, d: must_have_n_of(
                i, ['max', 'min', 'resolution'], num=0) if i.get(
                    'units', 'enum') in ['Boolean', 'time', 'enum'] else False,
            # enum must not have min, max
            lambda k, i, m, d: must_have_n_of(i, ['units'], num=0)
            if isinstance(i.get('enum', None), list) else False,
            # min must be less than max if present
            lambda k, i, m, d:
            f"min {i.get('min', False)} is not less than max {i.get('max', False)}"
            if (not isinstance(i.get('min', False), bool)) and
            (i.get('min', -math.inf) >= i.get('max', math.inf)) else False,
            # default must between min and max if numeric
            lambda k, i, m, d:
            f"default {i['default']} not between {i['min']} and {i['max']}"
            if (isinstance(i.get('default', False), numbers.Number) and not (
                i.get('min', -math.inf) <= i.get('default', False) <= i.get(
                    'max', math.inf))) else False,
            # must have valid c type
            lambda k, i, m, d: f"invalid C type {c_type(i)}"
            if c_type(i) not in ALLOWED_C_TYPES else False,
        ],
        'key_regex':
        '^[A-Z]+([A-Z0-9])*(_[A-Z0-9]+)*$',
    },
    'alarm': {
        'required': {
            'notes': {},
            'status': {
                'enum': ['core', 'proposed']
            },
            'source': {}
        },
        'optional': {
            'min': {
                'type': [int, float]
            },
            'max': {
                'type': [int, float]
            },
            'default': {
                'type': [int, float]
            },
        },
        'extra_checks': [
            # stripping the last underscore work (eg "_hi") must find a state value
            lambda k, i, m, d: foreign_key(alarm_to_state(k), 'state', d),
            # default must be between min and max
            lambda k, i, m, d:
            f"default {i['default']} not between {i['min']} and {i['max']}"
            if not (i['min'] <= i['default'] <= i['max']) else False,
        ],
        #
        'key_regex':
        '^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*(_(HI|LOW|DIV|DIFF))$',
    },
    'alarm_level': {
        'required': {
            'notes': {},
            'synonyms': {},
            'status': {
                'enum': ['core', 'proposed'],
            }
        },
        'optional': {},
        'key_regex': '^[A-Z]+$',
    },
    'mode': {
        'required': {
            'full': {},
        },
        'optional': {
            'notes': {},
        },
        'key_regex': '^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$',
    },
    'module': {
        'required': {
            'name': {},
            'called_by': {},
            'functions': {},
            'returns': {
                'enum': ALLOWED_C_TYPES
            }
        },
        'optional': {
            'notes': {}
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
        'required': {
            'full': {},
            'source': {},
        },
        'optional': {
            'definition': {},
        },
        'key_regex': '^[a-zA-Z0-9]*$',
    },
}


def load_yaml(source_dir=DICTIONARY_PATH):
    """
    Load the entire metadata into memory and return a dictionary
    """
    data = {}
    for chapter in META_ITEMS:  # loop over files
        yaml_text = open(yaml_file(source_dir, chapter), 'r')
        data[chapter] = yaml.load(yaml_text, Loader=UniqueKeyLoader)
    return data
