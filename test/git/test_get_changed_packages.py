try:
    from unittest import mock
except ImportError:
    import mock

import os
import subprocess
import sys

import scream.cli.main as scream
from scream import detect_changed_packages
from scream.files.setup import SetupCfg
from scream.utils import chdir
from test.base_tests import Base, MyPackage


class TestChangedPackages(Base.TestNewMonorepoGitInit):

    def test_get_parent_no_parent(self):
        with chdir(self.TMP_DIR):
            self.assertEqual(detect_changed_packages.get_parent_branch(), "master")

    def test_get_parent_branch(self):
        with chdir(self.TMP_DIR):
            subprocess.call(["git", "checkout", "-b", "otherbranch"])
            self.assertEqual(detect_changed_packages.get_parent_branch(), "master")

    def test_no_changed_packages(self):
        with chdir(self.TMP_DIR):
            parent_branch = detect_changed_packages.get_parent_branch()
            changed_files = detect_changed_packages.get_changed_files(
                parent_branch)

        self.assertEqual(changed_files, [], parent_branch)

    def test_changed_packages(self):
        expected_changes = [['A', 'packagea/setup.cfg']]

        with chdir(self.TMP_DIR):
            package_a = MyPackage(d=self.TMP_DIR, name="packagea")

            os.mkdir(package_a.name)
            SetupCfg(package_a.full_name).write(package_a.package_dir)

            subprocess.call(["git", "add", "."])

            parent_branch = detect_changed_packages.get_parent_branch()
            changed_files = detect_changed_packages.get_changed_files(parent_branch)

        self.assertEqual(changed_files, expected_changes, parent_branch)

    def test_parse_git_diff(self):
        input_example = """A	packagea/README.md\nA	packageb/README.md"""
        expected = [['A', "packagea/README.md"], ["A", "packageb/README.md"]]
        actual = detect_changed_packages.parse_git_diff(input_example)
        self.assertEqual(expected, actual)


class NoGitCommitsYetTestChangedPackages(Base.TestNewMonorepo):
    """
    Runs some tests to make sure nothing breaks prior to a user initializing a git repo.
    """

    def test_scream_test_gracefully_handle_no_git(self):
        with chdir(self.TMP_DIR):
            with mock.patch.object(sys, "argv", ["scream", "test"]):
                with self.assertRaises(SystemExit):
                    scream.Scream()
