"""WIP on the VentOS Extension Package (vep) system

Todo:

# lint a package
# lint a build
# render a package in markdown
# much much more...

"""
import re
import yaml
from validator_collection import checkers
import ventos_yaml as vy

REGEXES = { # {field: (regex, description), ...}
    "name": (
        "^[a-z][a-z0-9_]{3,19}$",
        "letter then lower case letters, numbers and underscore, "
        "4-20 characters"),
    "tag": (
        "^[a-z][a-z0-9.]{1,19}$",
        "letter then lower case letters, numbers and period, "
        "2-20 characters"),
    "title": (
        "^[A-Z][A-Za-z0-9- :,.]{3,39}$",
        "Title with limited puntuation, 4-40 characters"),
}

def get_core_hooks(meta_dfs):
    """ generate a list of all hooks """
    # generate a double list of pre and post hooks
    hooks = [[f"pre_{module}", f"post_{module}"]
             for module in meta_dfs['module'].index]
    # flatten list by adding them all together
    return sum(hooks, [])

def read_build(build_yaml_text):
    """ Convert a build text to python structure."""
    return yaml.load(build_yaml_text, Loader=vy.UniqueKeyLoader)

def lint_using_regexes(errors, fields, obj, regexes):
    """ Validate simple fields via regex """
    for field in fields:
        regex = regexes[field]
        key_pattern = re.compile(regex[0])
        value = obj.get(field, "")
        if not key_pattern.match(value):
            errors[field] = f'"{value}" is not {regex[1]}'

def lint_build(build):
    """ Lint the build python structure."""
    errors = {}
    lint_using_regexes(errors, ['name', 'tag', 'title'], build, REGEXES)
    # validate project_url
    field = 'project_url'
    value = build.get(field, "")
    if not checkers.is_url(value):
        errors[field] = f'"{value}" is not a valid URL'
    # validate veps:
    field = 'veps'
    value = build.get(field, [])
    if not isinstance(value, list):
        errors[field] = 'Package list (veps) is not a list'
    elif len(value) < 1:
        errors[field] = 'Empty package list'
    else:
        for vep_index, vep in enumerate(value):
            field = f"vep #{vep_index+1}"
            if not isinstance(vep, dict):
                errors[field] = 'Package list (veps) is not a dictionary'
            elif list(vep.keys()) != ['url']:
                print('vep.keys()', vep.keys())
                errors[field] = 'Invalid VEP'
            else:
                field = f"vep #{vep_index+1} url"
                url = vep.get('url', '')
                if not checkers.is_url(url):
                    errors[field] = 'is not a valid URL'
                elif not url.endswith('/vep.yaml'):
                    errors[field] = 'does not point to a vep.yaml file'
    return errors

def lint_vep(core_meta_dfs, vepo):
    """ Lint the VEP definition object """
    errors = {}
    # basic check of values agains regexes
    lint_using_regexes(errors, ['name', 'tag', 'title'], vepo, REGEXES)
    # check the hooks are valid
    field = 'hooks'
    value = vepo.get(field, [])
    if not isinstance(value, list):
        errors[field] = 'not a list'
    else:
        core_hooks = get_core_hooks(core_meta_dfs)
        unknown_hooks = [hook for hook in value if hook not in core_hooks]
        if len(unknown_hooks) > 0:
            errors[field] = f"unknown hooks: {', '.join(unknown_hooks)}"
    # check "state"
    field = 'state'
    value = vepo.get(field, {})
    if not isinstance(value, dict):
        print('value', value)
        errors[field] = 'not a dictionary'

    # At this stage only "state" can be extended by a VEP.
    # It is highly probable this will change.
    simple_meta_meta_extensions = ['state']
    core_extensions = {k: vepo.get(k, {}) for k in simple_meta_meta_extensions}
    meta_meta = {k: vy.META_META[k] for k in simple_meta_meta_extensions}
    # Do a simple check that the new items meet the existing rules.
    # This too may be too simple in the future
    errors.update(vy.lint_meta(core_extensions, meta_meta))
    return errors
