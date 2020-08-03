#!/usr/bin/python3.7
import yaml, pandas as pd
import ventos_yaml as vy

print("""
# Introduction
This is a simple output of the contents of the draft VentOS meta database.

Using YAML files committed git repositories the VentOS project is able to
control changes.

In the future this script will contain various transformation scripts.
""")

def snake_to_title(key):
    return key.replace('_', ' ').title()

def print_index(data):
    for chapter, meta in data.items():
        meta_meta = vy.meta_meta[chapter]
        print(f'\n# {snake_to_title(chapter)} ({len(meta)} items)')
        print(" | ".join((meta.keys())))
        cols = {**meta_meta['required'], **meta_meta['optional']}
        df = pd.DataFrame.from_dict(meta, orient='index',  columns=cols)
        print(df.to_markdown())

def main():
    data = vy.load_yaml()
    print_index(data)

if __name__ == "__main__":
    main()

