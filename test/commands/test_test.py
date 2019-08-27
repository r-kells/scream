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
            subprocess.call(["git", "checkout", "-b", "new_branch"])

            cls.package_a = MyPackage(d=cls.TMP_DIR, name="packagea", local_dependencies=[])

            os.mkdir(cls.package_a.name)
            SetupCfg(cls.package_a.package_name).write(cls.package_a.package_dir)

            subprocess.call(["git", "add", "."])

    def test_test_commands(self):
        cmds_and_expected_output = [
            ({"all_packages": [self.package_a], "package_name": None, 'parallel': True},
             ['tox', '-e', 'py37-company_packagea', '-p', 'all']),
            ({"all_packages": [self.package_a], "package_name": None, "dry_run": True}, None),
            ({"all": True, 'parallel': True}, ['tox', '-p', 'all']),
            ({"package_name": "packagea"}, ['tox', '-e', 'packagea']),
            ({"package_name": "packagea", "all": True}, ['tox', '-e', 'packagea'])
        ]
        with chdir(self.TMP_DIR):
            for cmd, expected in cmds_and_expected_output:
                test_cmd = build_test_cmd(**cmd)
                self.assertEqual(test_cmd, expected)
