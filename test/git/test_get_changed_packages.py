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
            subprocess.call(["git", "init"])

            package_name = "packagea"
            package_dir = os.path.join(TMP_DIR, package_name)
            scream.new_package(package_dir, namespaces=['company'], package_name=package_name)

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
            changed_files = detect_changed_packages.get_changed_files(parent_branch)

        self.assertEqual(changed_files, [], parent_branch)


# subprocess.call(["git", "checkout", "-b", parent_branch])
# subprocess.call(["git", "add", "."])
# subprocess.call(["git", "commit", "-m", "ok"])