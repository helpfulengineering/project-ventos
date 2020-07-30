#!/usr/bin/python3.7
import yaml, os
path = 'datadictionary'
print(f"# package generation stub from {os.getcwd()}")
print("""This script does nothing useful, but acts as a placeholder for future transformation scripts.
        """)
files = ['alarms', 'abbreviations']
data = {}
for f in files:
    yaml_text = open(os.path.join(path, f'{f}.yaml'), 'r').read()
    data[f] = yaml.load(yaml_text)
    print(f'\n## {f} keys')
    print("\n".join((data[f].keys())))

