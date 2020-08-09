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

Ulimately the tests will occur early in the integration pipeline, with the
packaging occurring in later steps.

# Development Tips

The [`makefile`](../makefile) provides useful shortcuts, some of which assume that you have a sibling directory located at `../ventosdoc`.

Executing two seperate watches is seperate terminal windows makes editing the
files easier, using these commands from the root directory of the project (NOT
this directory):


    make dev-watch-lint

and

    make dev-watch-test


You can then run this to output the generated files:

    make yaml-package

