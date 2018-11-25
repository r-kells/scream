"""
Tests the user endpoints directly
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

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(PARENT_DIR, 'tmp')


class TestUserExperience(unittest.TestCase):

    @classmethod
    def setUp(cls):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)
        with chdir(TMP_DIR):
            # The user is required to setup git to get the most out of `scream test` and `scream build`.
            subprocess.call(["git", "config", "user.email", "ryan.kelly.md@gmail.com"])
            subprocess.call(["git", "config", "user.name", "Ryan Kelly"])

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "init monorepo!"])

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


class TestUserExperienceNoGit(unittest.TestCase):
    """
    Runs some tests to make sure nothing breaks prior to a user initializing a git repo.
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

    def test_scream_test_gracefully_handle_no_git(self):
        with chdir(TMP_DIR):
            with mock.patch.object(sys, "argv", ["scream", "test"]):
                with self.assertRaises(SystemExit):
                    scream.Scream()
