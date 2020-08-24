"""Test for the VentOS Extension Package (vep) system"""
import ventos_yaml as vy
import package
import vep

def get_core_meta_dfs():
    """Get the core meta data"""
    core_yaml = vy.load_yaml()
    return package.meta_to_dataframes(core_yaml, pretty=False)

TEST_BUILD_YAML = """
name: test_build_1
tag: v0.0.1
title: "VentOS Test Build"
project_url: https://gitlab.com/project-ventos/ventos
veps:
  - url: https://gitlab.com/project-ventos/ventos/-/raw/datadictionary/test_vep1/vep.yaml
  - url: https://gitlab.com/project-ventos/ventos/-/raw/datadictionary/test_vep2/vep.yaml
  - url: https://raw.githubusercontent.com/ErichBSchulz/test_vep3/v0.0.1/vep.yaml
"""


def test_lint_build():
    """ initial test WIP """
    build = vep.read_build(TEST_BUILD_YAML)
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 0
    build['name'] += " new"
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 1
    build['project_url'] += " badspace"
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 2
    build['veps'].append({'url': 'https://example.com/vep.yaml'})
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 2
    build['veps'].append({'url': 'https://example.com/vep.yml'})
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 3
    build = vep.read_build(TEST_BUILD_YAML)
    del build['veps']
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 1
    build = vep.read_build(TEST_BUILD_YAML)
    del build['name']
    lint_errors = vep.lint_build(build)
    assert len(lint_errors) == 1

# Example VEP definition
TEST_VEP_YAML_1 = """
name: test_vep_1
tag: v0.0.5
title: Test VEP 1
hooks:
  - pre_LOG
  - post_DISPLAY
state:
  CHAMBER:
    status: draft
    notes: Chamber pressure
    sot: sensor
    units: mBar
    min: 0
    max: 10000
    resolution: 1
  MOTOR_TEMP:
    status: draft
    notes: Motor temperature
    sot: sensor
    units: Celsius
    min: 0
    max: 1000
    resolution: 0.1
"""

def test_lint_vep():
    """ Test the VEP linter, starting with a good example then breaking it."""
    core_meta_dfs = get_core_meta_dfs()
    def expect_error_after_linting(expected_error_count, vepo):
        lint_errors = vep.lint_vep(core_meta_dfs, vepo)
        assert len(lint_errors) == expected_error_count

    vepo = vep.read_build(TEST_VEP_YAML_1)
    expect_error_after_linting(0, vepo)
    vepo['name'] = "bad name"
    expect_error_after_linting(1, vepo)
    vepo['hooks'].append('bad_hook')
    expect_error_after_linting(2, vepo)
    vepo['state']['CHAMBER']['units'] = 'frogs'
    expect_error_after_linting(3, vepo)
    vepo['state']['CHAMBER']['max'] = -1
    expect_error_after_linting(4, vepo)
