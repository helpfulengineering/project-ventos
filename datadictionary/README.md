# VentOS Data Dictionary

Here in lies the central beating heart of VentOS, in the form of
meta-data stored in inter-linked [YAML files](https://yaml.org/).

The python [`test_lint`](test_lint.py) is a [pytest](https://docs.pytest.org/en/stable/getting-started.html)
that performs syntax and referential integrity checks, although if you follow
the patterns described in the file you should be OK.

Running `pytest` in the project root directory should execute all tests.

Numerous other formats of the core information within the YAML are produced by
the [`package`](package.py) script.

This is all a work in progress, and as the project evolves, so will these two
scripts.
