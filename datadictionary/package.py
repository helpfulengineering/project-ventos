#!/usr/bin/python3.7
import yaml, pandas as pd, math, re
from textwrap import dedent
import ventos_yaml as vy

def snake_to_title(key):
    return key.replace('_', ' ').title()

def print_main_md(data):
    print(dedent("""
    # <a name='top'></a>Introduction
    This is a simple output of the contents of the draft VentOS meta database.

    Using YAML files committed git repositories the VentOS project is able to
    control changes.

    In the future this script will contain various transformation scripts.
    """))

    # header bar
    print(" | ".join([f"*[{snake_to_title(c)}](#{c})*" for c in data.keys()]))
    for chapter, meta in data.items():
        meta_meta = vy.meta_meta[chapter]
        print(f'\n# <a name="{chapter}"></a>{snake_to_title(chapter)} '
              f'({len(meta)} items)')
        print(" | ".join((meta.keys())))
        cols = {**meta_meta['required'], **meta_meta['optional']}
        df = pd.DataFrame.from_dict(meta, orient='index',  columns=cols)
        if chapter == 'state':
            # make a pretty cell
            range_cols = ['min', 'max', 'units', 'enum', 'default']
            df['values'] = [
                    ("" if pd.isnull(r.default) else f"{r.default} " ) +
                    (f"({', '.join(r.enum)}) " if type(r.enum)==list
                        else ('' if r.units in ['time', 'Boolean']
                            else f"({r.min}-{r.max}) ") + f"{r.units}")
                    for r in df.itertuples()]
            # create a list of alarms this property links to
            df['alarms'] = [
                    ', '.join([k for k in data['alarm'].keys()
                                 if re.match(f"{r.Index}_[A-Z]*", k)])
                    for r in df.itertuples()]
            df.drop(range_cols, axis=1, inplace=True)
        elif chapter == 'alarm':
            df['units'] = [
                    data['state'][vy.alarm_to_state(r.Index)]['units']
                    for r in df.itertuples()]
        print(df.to_markdown(showindex=True))
        print('\n[[top]](#top)')

def main():
    data = vy.load_yaml()
    print_main_md(data)

if __name__ == "__main__":
    main()

