""" Tests for the YAML library """
import os
import glob
import ventos_yaml as vy
import package


def test_all_files_have_meta():
    """Check the YAML file list exactly matches the metadata"""
    def base(fname):
        return os.path.splitext(os.path.basename(fname))[0]

    dictionary_yaml_glob = glob.glob(vy.yaml_file(vy.DICTIONARY_PATH, '*'))
    files = [base(fname) for fname in dictionary_yaml_glob]
    assert set(files) == set(vy.META_META.keys())


def test_lint():
    """Lint all YAML files according to the meta-meta-data from `ventos_yaml`"""
    meta = vy.load_yaml()
    # generic linting
    errors = vy.lint_meta(meta, vy.META_META)
    assert len(errors) == 0


def test_package():
    """
    Note this test does not include writing the files or verifying file
    timestamps or size etc
    """
    package.main({'sourcedir': vy.DICTIONARY_PATH, 'job': ['All']})
