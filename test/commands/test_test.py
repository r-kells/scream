import os
import subprocess

from scream.commands.test import build_test_cmd
from scream.files.setup import SetupCfg
from scream.utils import chdir
from test.base_tests import Base, MyPackage


class TestPackages(Base.TestNewMonorepoGitInit):

    @classmethod
    def setUp(cls):
        super(TestPackages, cls).setUp()
        # Create a fake package that's available to test.
        with chdir(cls.TMP_DIR):
            package_a = MyPackage(d=cls.TMP_DIR, name="packagea")

            os.mkdir(package_a.name)
            SetupCfg(package_a.full_name).write(package_a.package_dir)

            subprocess.call(["git", "add", "."])

    def test_test_commands(self):
        cmds_and_expected_output = [
            ({"package_name": None}, ['tox', '-e', 'py36-company_packagea']),
            ({"package_name": None, "dry_run": True}, None),
            ({"all": True}, ['tox']),
            ({"package_name": "packagea"}, ['tox', '-e', 'packagea']),
            ({"package_name": "packagea", "all": True}, ['tox', '-e', 'packagea'])
        ]
        with chdir(self.TMP_DIR):
            for cmd, expected in cmds_and_expected_output:
                test_cmd = build_test_cmd(**cmd)
                self.assertEqual(test_cmd, expected)
