import os
import shutil
import subprocess
import unittest

import scream.cli.main as scream
from scream.utils import chdir
from scream import detect_changed_packages

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(PARENT_DIR, 'tmp')


class TestChangedPackages(unittest.TestCase):

    @classmethod
    def setUp(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)
        with chdir(TMP_DIR):
            scream.init_monorepo(TMP_DIR)
            subprocess.call(["git", "config", "user.email", "ryan.kelly.md@gmail.com"])
            subprocess.call(["git", "config", "user.name", "Ryan Kelly"])

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "init monorepo!"])

    @classmethod
    def tearDown(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_get_parent_no_parent(self):
        with chdir(TMP_DIR):
            self.assertEqual(detect_changed_packages.get_parent_branch(), "master")

    def test_get_parent_branch(self):
        with chdir(TMP_DIR):
            subprocess.call(["git", "checkout", "-b", "otherbranch"])
            self.assertEqual(detect_changed_packages.get_parent_branch(), "master")

    def test_no_changed_packages(self):
        with chdir(TMP_DIR):
            parent_branch = detect_changed_packages.get_parent_branch()
            changed_files = detect_changed_packages.get_changed_files(
                parent_branch)

        self.assertEqual(changed_files, [], parent_branch)

    def test_changed_packages(self):
        packagea_name = "packagea"
        packagea_dir = os.path.join(TMP_DIR, packagea_name)

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

        with chdir(TMP_DIR):
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
