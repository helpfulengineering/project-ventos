#!/usr/bin/python3.7
import yaml, os
import pprint, inspect

path = 'datadictionary'
p = pprint.pprint
print(f"hello world! from {os.getcwd()}")
alarm_yaml = open(os.path.join(path, 'alarms.yaml'), 'r').read()
abbreviation_yaml = open(os.path.join(path, 'abbreviations.yaml'), 'r').read()

alarms = yaml.load(alarm_yaml)
abbreviations = yaml.load(abbreviation_yaml)

print(f"#RAW:\n{alarm_yaml}")
p(alarms)
# p(abbreviations)

