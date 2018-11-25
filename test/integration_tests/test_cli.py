"""
Tests the user endpoints directly.
TODO capture logging output to verify exactly what is happening.
"""
try:
    from unittest import mock
except ImportError:
    import mock

import os
import shutil
import subprocess
import sys
import unittest

import scream.cli.main as scream
from scream.utils import chdir

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(PARENT_DIR, 'tmp')


class TestCliInitMonorepo(unittest.TestCase):
    """Make sure `scream init` runs, and all other commands gracefully fail if `scream init` hasn't run.
    """

    @classmethod
    def setUp(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)

    @classmethod
    def tearDown(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_init_monorepo(self):
        with chdir(TMP_DIR):
            with mock.patch.object(sys, "argv", ["scream", "init"]):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

    def test_cmd_b4_init_monorepo(self):
        test_command = ["scream", "test"]
        new_command = ["scream", "new", "company.packagea"]
        install_command = ["scream", "install", "company_packagea"]

        cmds = [test_command, new_command, install_command]

        with chdir(TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 1)


class TestCliNew(unittest.TestCase):
    """Make sure all `scream new` commands run.
    """
    cmd = ["scream", "new", "company.packagea"]

    @classmethod
    def setUp(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)
        with chdir(TMP_DIR):
            scream.init_monorepo(TMP_DIR)
            # The user is required to setup git to get the most out of `scream test` and `scream build`.
            subprocess.call(["git", "config", "user.email", "ryan.kelly.md@gmail.com"])
            subprocess.call(["git", "config", "user.name", "Ryan Kelly"])

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "init monorepo!"])

    @classmethod
    def tearDown(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_new_package(self):

        with chdir(TMP_DIR):
            with mock.patch.object(sys, "argv", self.cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)


class TestCliTest(unittest.TestCase):
    """Make sure all `scream test` commands run, with or without any packages existing.
    """
    test = ["scream", "test"]
    test_package = ["scream", "test", "--name", "company_packagea", "--dry-run"]
    test_dry = ["scream", "test", "--dry-run"]
    test_all = ["scream", "test", "--all", "--dry-run"]

    @classmethod
    def setUp(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)
        with chdir(TMP_DIR):
            scream.init_monorepo(TMP_DIR)
            # The user is required to setup git to get the most out of `scream test` and `scream build`.
            subprocess.call(["git", "config", "user.email", "ryan.kelly.md@gmail.com"])
            subprocess.call(["git", "config", "user.name", "Ryan Kelly"])

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "init monorepo!"])

    @classmethod
    def tearDown(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_test_no_packages_created(self):

        cmds = [self.test, self.test_package, self.test_all, self.test_dry]

        with chdir(TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)

    def test_test_with_packages_created(self):
        cmd = ["scream", "new", "com.packagea"]

        with chdir(TMP_DIR):
            # Add a package.
            with mock.patch.object(sys, "argv", cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

            subprocess.call(["git", "add", "."])

        cmds = [self.test_package, self.test_all, self.test_dry]

        with chdir(TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)


class TestCliInstall(unittest.TestCase):
    """Make sure all `scream install` commands run, with or without any packages existing.
    """
    cmd = ["scream", "install", "com_packagea"]

    @classmethod
    def setUp(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)
        with chdir(TMP_DIR):
            scream.init_monorepo(TMP_DIR)
            # The user is required to setup git to get the most out of `scream test` and `scream build`.
            subprocess.call(["git", "config", "user.email", "ryan.kelly.md@gmail.com"])
            subprocess.call(["git", "config", "user.name", "Ryan Kelly"])

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "init monorepo!"])

    @classmethod
    def tearDown(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_install_no_packages_created(self):

        with chdir(TMP_DIR):
            with mock.patch.object(sys, "argv", self.cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 1)

    def test_install_with_packages_created(self):
        cmd = ["scream", "new", "com.packagea"]

        with chdir(TMP_DIR):
            # Add a package.
            with mock.patch.object(sys, "argv", cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

            subprocess.call(["git", "add", "."])

        with chdir(TMP_DIR):
            with mock.patch.object(sys, "argv", self.cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)
