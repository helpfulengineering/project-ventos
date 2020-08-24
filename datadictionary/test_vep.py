"""Test for the VentOS Extension Package (vep) system"""
import ventos_yaml as vy
import package
import vep

def get_core_meta_dfs():
    """Get the core meta data"""
    core = vy.load_yaml()
    return package.meta_to_dataframes(core, pretty=False)

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
    """ Lint the build buy starting with a good one then repeatedly breaking
    it"""
    def expect_error_after_linting(expected_error_count, build):
        lint_errors = vep.lint_build(build)
        assert len(lint_errors) == expected_error_count
    build = vep.read_yaml(TEST_BUILD_YAML)
    expect_error_after_linting(0, build)
    build['name'] += " new"
    expect_error_after_linting(1, build)
    build['project_url'] += " badspace"
    expect_error_after_linting(2, build)
    build['veps'].append({'url': 'https://example.com/vep.yaml'})
    expect_error_after_linting(2, build)
    build['veps'].append({'url': 'https://example.com/vep.yml'})
    expect_error_after_linting(3, build)
    build = vep.read_yaml(TEST_BUILD_YAML)
    del build['veps']
    expect_error_after_linting(1, build)
    build = vep.read_yaml(TEST_BUILD_YAML)
    del build['name']
    expect_error_after_linting(1, build)

# Example VEP definitions
TEST_VEP_YAML = ["""
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
""", """
name: test_vep_2
tag: v1.0
title: Test VEP 2 Xenon
hooks:
  - pre_LOG
  - pre_SENSE
  - pre_DISPLAY
state:
  XENON:
    status: draft
    notes: Inspired Xenon concentration
    sot: sensor
    units: percent
    min: 0
    max: 100
    resolution: 1
""", """
name: test_vep_3
tag: v0.0.1
title: Test VEP 3 Rhubarb
hooks:
  - pre_LOG
  - post_SENSE
  - pre_DISPLAY
state:
  RHUBARB:
    status: draft
    notes: Inspired Rhubarb concentration
    sot: sensor
    units: percent
    min: 0
    max: 100
    resolution: 1
"""]

def test_lint_vep():
    """ Test the VEP linter, starting with a good example then breaking it."""
    core_meta_dfs = get_core_meta_dfs()
    def expect_error_after_linting(expected_error_count, vepo):
        lint_errors = vep.lint_vep(core_meta_dfs, vepo)
        assert len(lint_errors) == expected_error_count

    vepo = vep.read_yaml(TEST_VEP_YAML[0])
    expect_error_after_linting(0, vepo)
    vepo['name'] = "bad name"
    expect_error_after_linting(1, vepo)
    # bad hook
    vepo['hooks'].append('bad_hook')
    expect_error_after_linting(2, vepo)
    # illegal units
    vepo['state']['CHAMBER']['units'] = 'frogs'
    expect_error_after_linting(3, vepo)
    # make the max less than the min
    vepo['state']['CHAMBER']['max'] = -1
    expect_error_after_linting(4, vepo)

def test_build():
    """ assemble a full build """
    core = vy.load_yaml()
    base_line_state_var_count = len(core['state'])
    build = vep.assemble_build_definitions(
        core, TEST_BUILD_YAML, TEST_VEP_YAML)
    assert len(build['hooks']) == 3
    # there are a total of 4 new state variables defined in the test cases
    assert len(build['state']) == base_line_state_var_count + 4
    # expect description to be 4 lines long at verbosity = 1
    # (1 line for title, and one for each VEP)
    description = vep.describe_build(build, verbosity=1)
    assert description.count('\n') + 1 == 4
    # verbose descriptions adds three lines for hooks and a line for state
    description = vep.describe_build(build, verbosity=3)
    assert description.count('\n') + 1 == 8
