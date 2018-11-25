try:
    from unittest import mock
except ImportError:
    import mock

import os
import subprocess
import sys

import scream.cli.main as scream
from scream import detect_changed_packages
from scream.utils import chdir
from test.base_tests import Base


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
        packagea_name = "packagea"
        packagea_dir = os.path.join(self.TMP_DIR, packagea_name)

        expected_changes = [
            ['A', 'packagea/README.md'],
            ['A', 'packagea/company/__init__.py'],
            ['A', 'packagea/company/packagea/__init__.py'],
            ['A', 'packagea/company/packagea/module.py'],
            ['A', 'packagea/setup.cfg'],
            ['A', 'packagea/setup.py'],
            ['A', 'packagea/tests/__init__.py'],
            ['A', 'packagea/tests/test_module.py']
        ]

        with chdir(self.TMP_DIR):
            # Add a package.
            scream.new_package(
                packagea_dir,
                namespaces=['company'],
                package_name=packagea_name)

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
