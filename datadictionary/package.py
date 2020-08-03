#!/usr/bin/python3.7
import yaml, os
import ventos_yaml as vy
path = 'datadictionary'
print(f"# package generation stub from {os.getcwd()}")
print("""This script does nothing useful, but acts as a placeholder for future transformation scripts.
        """)
files = ['alarm', 'abbreviation']
data = vy.load_yaml()
for f in files:
    print(f'\n## {f} keys')
    print("\n".join((data[f].keys())))

