#!/usr/bin/python3.7
import yaml, pandas as pd, math, re
from textwrap import dedent
import ventos_yaml as vy

def snake_to_title(key):
    return key.replace('_', ' ').title()


def print_main_md(data):
    # create a URL just by joining a list eg [state, peep] => state_peep
    url = lambda i : "_".join(i)
    # create a HTML anchor
    anchor = lambda i : f'<a name="{url(i)}"></a>'
    # create a markdown anchor using the last item in the list as the label
    link = lambda k : f'[{k[-1]}](#{url(k)})'

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
        print(f'\n# {anchor([chapter])}{snake_to_title(chapter)} '
              f'({len(meta)} items)')
        print(" | ".join([link([chapter, k]) for k in meta.keys()]))
        cols = {**meta_meta['required'], **meta_meta['optional']}
        df = pd.DataFrame.from_dict(meta, orient='index',  columns=cols)
        # modify the data-frame to make it prettier and add links and achnors
        if chapter == 'state':
            # make a pretty cell
            # calculate precision
            df['significant_digits'] = [(max(0, -round(math.log10(r.resolution)))
                    if vy.isNumber(r.resolution) else 0)
                    for r in df.itertuples()]
            df['values'] = [vy.pretty_values(r) for r in df.itertuples()]
            df['c_type'] = [vy.c_type(r) for r in df.itertuples()]
            # create a list of alarms this property links to
            df['alarms'] = [
                    ', '.join([f"[{k}](#{url(['alarm', k])})" for k in data['alarm'].keys()
                                 if re.match(f"{r.Index}_[A-Z]*", k)])
                    for r in df.itertuples()]
            range_cols = ['min', 'max', 'units', 'enum', 'default', 'significant_digits', 'resolution']
            df.drop(range_cols, axis=1, inplace=True)
            #print(df[['significant_digits', 'values', 'default', 'c_type']].to_markdown())
        elif chapter == 'alarm':
            # link back to the alarm state
            df['state'] = [link(['state', vy.alarm_to_state(r.Index)]) for r in df.itertuples()]
            # links to state and join the units fields
            df['units'] = [
                    data['state'][vy.alarm_to_state(r.Index)]['units']
                    for r in df.itertuples()]
        df['key'] = [anchor([chapter, r.Index]) for r in df.itertuples()]
        print(df.to_markdown(showindex=True))
        print('\n[[top]](#top)')

def main():
    data = vy.load_yaml()
    print_main_md(data)

if __name__ == "__main__":
    main()


