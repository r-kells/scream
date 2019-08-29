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
    """Make sure `scream init` runs, and all other commands gracefully fail.
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
    test_package = ["scream", "test", "--package-name", "company_packagea", "--dry-run"]
    test_dry = ["scream", "test", "--dry-run"]
    test_all = ["scream", "test", "--all", "--dry-run"]
    test_parallel = ["scream", "test", "--all", "--dry-run", "--parallel"]

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

        cmds = [self.test_package, self.test_all, self.test_dry, self.test_parallel]

        with chdir(self.TMP_DIR):
            for cmd in cmds:
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)


class TestCliInstall(Base.TestNewMonorepoGitInit):
    """Make sure all `scream install` commands run, with or without any packages existing.
    """
    basic_cmd = ["scream", "install", "com_packagea"]
    test_cmd = ["scream", "install", "com_packagea", "--test"]
    test_cmd_short = ["scream", "install", "com_packagea", "-t"]

    install_cmds = [basic_cmd, test_cmd, test_cmd_short
                    ]

    def test_install_no_packages_created(self):
        for cmd in self.install_cmds:
            with chdir(self.TMP_DIR):
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 1)

    def test_install_with_packages_created(self):
        new_cmd = ["scream", "new", "com.packagea"]

        with chdir(self.TMP_DIR):
            # Add a package.
            with mock.patch.object(sys, "argv", new_cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

            subprocess.call(["git", "add", "."])

        for cmd in self.install_cmds:
            with chdir(self.TMP_DIR):
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)


class TestCliDeploy(Base.TestNewMonorepoGitInit):
    """Make sure all `scream deploy` commands run, with or without any packages existing.
    """
    deploy_cmd = ["scream", "deploy", "--package-name", "packagea"]
    deploy_all_cmd = ["scream", "deploy"]
    deploy_cmds = [deploy_cmd, deploy_all_cmd]

    def test_deploy_no_packages_created(self):
        with chdir(self.TMP_DIR):
            with mock.patch.object(sys, "argv", self.deploy_cmd):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

    def test_deploy_with_packages_created(self):
        create = ["scream", "new", "com.packagea"]

        with chdir(self.TMP_DIR):
            # Add a package.
            with mock.patch.object(sys, "argv", create):
                with self.assertRaises(SystemExit) as err:
                    scream.Scream()
                self.assertEqual(err.exception.code, 0)

            subprocess.call(["git", "add", "."])

        for cmd in self.deploy_cmds:
            with chdir(self.TMP_DIR):
                with mock.patch.object(sys, "argv", cmd):
                    with self.assertRaises(SystemExit) as err:
                        scream.Scream()
                    self.assertEqual(err.exception.code, 0)
