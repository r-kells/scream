import os
import shutil
import subprocess
import unittest

import scream.cli.main as scream
from scream.utils import chdir

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(PARENT_DIR, 'tmp')


class Base(object):
    class TestNewMonorepo(unittest.TestCase):
        """Make sure knows how to setup and tear down a new monorepo directory
        """
        TMP_DIR = TMP_DIR

        @classmethod
        def setUp(cls):
            if os.path.isdir(cls.TMP_DIR):
                shutil.rmtree(cls.TMP_DIR)

            os.mkdir(cls.TMP_DIR)

        @classmethod
        def tearDown(cls):
            if os.path.isdir(cls.TMP_DIR):
                shutil.rmtree(cls.TMP_DIR)

    class TestNewMonorepoGitInit(TestNewMonorepo):
        """Make sure knows how to setup and tear down a new monorepo directory
        """
        TMP_DIR = TMP_DIR

        @classmethod
        def setUp(cls):
            super(Base.TestNewMonorepoGitInit, cls).setUp()
            with chdir(cls.TMP_DIR):
                scream.init_monorepo(cls.TMP_DIR)
                # The user is required to setup git to get the most out of `scream test` and `scream build`.
                subprocess.call(["git", "config", "user.email", "ryan.kelly.md@gmail.com"])
                subprocess.call(["git", "config", "user.name", "Ryan Kelly"])

                subprocess.call(["git", "add", "."])
                subprocess.call(["git", "commit", "-m", "init monorepo!"])

        @classmethod
        def tearDown(cls):
            super(Base.TestNewMonorepoGitInit, cls).tearDown()
