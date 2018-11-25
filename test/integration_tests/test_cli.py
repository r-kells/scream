"""
Tests the user endpoints directly.
TODO capture logging output to verify exactly what is happening.
"""
try:
    from unittest import mock
except ImportError:
    import mock

import subprocess
import sys

import scream.cli.main as scream
from scream.utils import chdir
from test.base_tests import Base


class TestCliInitMonorepo(Base.TestNewMonorepo):
    """Make sure `scream init` runs, and all other commands gracefully fail if `scream init` hasn't run.
    """

    def test_init_monorepo(self):
        with chdir(self.TMP_DIR):
            with mock.patch.object(sys, "argv", ["scream", "init"]):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

    def test_cmd_b4_init_monorepo(self):
        test_command = ["scream", "test"]
        new_command = ["scream", "new", "company.packagea"]
        install_command = ["scream", "install", "company_packagea"]

        cmds = [test_command, new_command, install_command]

        with chdir(self.TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 1)


class TestCliNew(Base.TestNewMonorepoGitInit):
    """Make sure all `scream new` commands run.
    """
    cmd = ["scream", "new", "company.packagea"]

    def test_new_package(self):
        with chdir(self.TMP_DIR):
            with mock.patch.object(sys, "argv", self.cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)


class TestCliTest(Base.TestNewMonorepoGitInit):
    """Make sure all `scream test` commands run, with or without any packages existing.
    """
    test = ["scream", "test"]
    test_package = ["scream", "test", "--name", "company_packagea", "--dry-run"]
    test_dry = ["scream", "test", "--dry-run"]
    test_all = ["scream", "test", "--all", "--dry-run"]

    def test_test_no_packages_created(self):

        cmds = [self.test, self.test_package, self.test_all, self.test_dry]

        with chdir(self.TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)

    def test_test_with_packages_created(self):
        cmd = ["scream", "new", "com.packagea"]

        with chdir(self.TMP_DIR):
            # Add a package.
            with mock.patch.object(sys, "argv", cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

            subprocess.call(["git", "add", "."])

        cmds = [self.test_package, self.test_all, self.test_dry]

        with chdir(self.TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)


class TestCliInstall(Base.TestNewMonorepoGitInit):
    """Make sure all `scream install` commands run, with or without any packages existing.
    """
    cmd = ["scream", "install", "com_packagea"]

    def test_install_no_packages_created(self):
        with chdir(self.TMP_DIR):
            with mock.patch.object(sys, "argv", self.cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 1)

    def test_install_with_packages_created(self):
        cmd = ["scream", "new", "com.packagea"]

        with chdir(self.TMP_DIR):
            # Add a package.
            with mock.patch.object(sys, "argv", cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

            subprocess.call(["git", "add", "."])

        with chdir(self.TMP_DIR):
            with mock.patch.object(sys, "argv", self.cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)
