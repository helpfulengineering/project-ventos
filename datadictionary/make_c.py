"""Library for converting metadata into VentOS C code"""
from textwrap import wrap, dedent

def comment(text):
    """ Make a C comment. Returns text."""
    pre = '      // '
    return pre + ('\n'+ pre).join(wrap(text, width=70)) + '\n' if text else ''

def format_vars(rec):
    """ Make a C structure variable, based on notes, c_type and Index.
    Returns text."""
    return comment(rec.notes) + f"      {rec.c_type} {rec.Index};"

def make_state_struct(meta_dfs):
    """ Make a C struct based on the state dataframe. Returns text."""
    state_vars = "\n" + "\n".join(
        [format_vars(rec) for rec in meta_dfs['state'].itertuples()])
    # note use of {{double curlies}} to escape {} in python f"string"
    c_text = f"""
    struct state
    {{{state_vars}
    }};
    """
    return c_text

def make_all_module_stubs(meta_dfs):
    """ Make all basic VentOS definition. """
    "Example that assume a VEP call SUPER_PRVC, and BLUETOOTH"
    example_hooks = {
        'SUPER_PRVC': {
            'post_THINK': {'weight': 60.0},
            'pre_LOG': {'weight': 50.0},
            },
        'BLUETOOTH': {
            'post_LOG': {'weight': 50.0},
            'post_THINK': {'weight': 50.0},
            }}

    def make_module_hooks(all_hooks):
        """ reorder a list of hooks organised by VEPS, to a list organised by
        hook name"""
        hooks = {}
        for VEP, vep_hooks in example_hooks.items():
            for hook, hook_meat in vep_hooks.items():
                if not hook in hooks:
                    hooks[hook] = []
                hooks[hook].append({'VEP': VEP, **hook_meat})
        return hooks

    module_hooks = make_module_hooks(example_hooks)

    return '\n'.join(
        make_module_stub(module, rec, module_hooks)
        for module, rec in meta_dfs['module'].iterrows())

def specific_hook_c(prefix, module, all_hooks):
    sh = sorted(all_hooks.get(f"{prefix}_{module}", []),
        key = lambda h: f'{h["weight"]:08.5}{h["VEP"]}')
    return [f"hook_{prefix}_{module}_{hook['VEP']}(state);" for hook in sh
            ] if len(sh) > 0 else [f'; // no {prefix}_{module} hooks']

def make_module_stub(module, meta, all_hooks):
    """ Make a basic VentOS definition. """
    indent = '\n      '
    c_text = dedent(f"""
    void {module}(struct State *state)
    {{
      hook_pre_{module}(state); // call all pre hooks
      core_{module}(state); // call core code
      hook_post_{module}(state); // call all post hooks
    }}

    void hook_pre_{module}(struct State *state)
    {{
      {indent.join(specific_hook_c('pre', module, all_hooks))}
    }}

    void hook_post_{module}(struct State *state)
    {{
      {indent.join(specific_hook_c('post', module, all_hooks))}
    }}""")
    return c_text
