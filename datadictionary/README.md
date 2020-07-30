# VentOS Data Dictionary

Here in lies the central beating heart of VentOS, in the form of
meta-data stored in inter-linked [YAML files](https://yaml.org/).

The python [`lint`](lint.py) script performs syntax and referential integrity checks, although if you follow the patterns described in the file you should be OK.

Numerous other formats of the core information within the YAML are produced by
the [`package`](package.py) script.

This is all a work in progress, and as the project evolves, so will these two
scripts.
