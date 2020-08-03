import yaml, os, re, glob, math

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
            },
        'extra_checks': [
            # must have either unit or enum, but not both
            lambda k,i,m,d: must_have_n_of(i, ['units', 'enum']),
            # config and operator variables must have a default
            lambda k,i,m,d: must_have_n_of(i, ['default'], n=1) if i['sot'] in ['config', 'operator'] else False,
            # must have min and max if not enum, Bool or time units
            lambda k,i,m,d: must_have_n_of(i, ['max', 'min'], n=2) if
               i.get('units', 'enum') not in ['Boolean', 'time', 'enum'] else False,
            # enum, Bool and time must not have min, max
            lambda k,i,m,d: must_have_n_of(i, ['max', 'min'], n=0) if
               i.get('units', 'enum') in ['Boolean', 'time', 'enum'] else False,
            # enum must not have min, max
            lambda k,i,m,d: must_have_n_of(i, ['units'], n=0) if type(i.get('enum', None)) == list else False,
            # min must be less than max if present
            lambda k,i,m,d: f"min {i.get('min', False)} is not less than max {i.get('max', False)}" if
                    (not isinstance(i.get('min', False), bool)) and (i.get('min', -math.inf) >= i.get('max', math.inf)) else False,
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
        'optional': {},
        'extra_checks': [
            # stripping the last underscore work (eg "_hi") must find a state value
            lambda k,i,m,d: foreign_key(k.rsplit('_', 1)[0], 'state', d)
            ],
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

# load the entire metadata into memory and return
def load_yaml():
    data = {}
    for f, meta in meta_meta.items(): # loop over files
        yaml_text = open(yaml_file(f), 'r')
        data[f] = yaml.load(yaml_text, Loader=UniqueKeyLoader)
    return data

