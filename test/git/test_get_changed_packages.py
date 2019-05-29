try:
    from unittest import mock
except ImportError:
    import mock

import os
import subprocess
import sys

import scream.cli.main as scream
from scream import detect_changed_packages
from scream.files import File
from scream.files.setup import SetupCfg
from scream.utils import chdir
from test.base_tests import Base, MyPackage


class TestChangedPackages(Base.TestNewMonorepoGitInit):

    # def test_get_parent(self):
    #     with chdir(self.TMP_DIR):
    #         self.assertEqual(detect_changed_packages.get_parent_branch(), "HEAD~1")

    def test_no_changed_packages(self):
        with chdir(self.TMP_DIR):
            changed_files = detect_changed_packages.get_changed_packages()

        self.assertEqual(changed_files, {})

    def test_changed_files(self):
        expected_changes = [['A', 'packagea/setup.cfg']]

        with chdir(self.TMP_DIR):
            subprocess.call(["git", "checkout", "-b", "example_feature"])

            package_a = MyPackage(d=self.TMP_DIR, name="packagea")

            os.mkdir(package_a.name)
            SetupCfg(package_a.package_name).write(package_a.package_dir)

            subprocess.call(["git", "add", "."])

            parent_branch = detect_changed_packages.get_parent_branch()
            changed_files = detect_changed_packages.get_changed_files(parent_branch)

        self.assertEqual(changed_files, expected_changes, parent_branch)

    def test_changed_packages(self):
        expected_changes = ["company_packagea", "company_packageb"]

        with chdir(self.TMP_DIR):
            subprocess.call(["git", "checkout", "-b", "new_branch"])

            package_a = MyPackage(d=self.TMP_DIR, name="packagea")

            os.mkdir(package_a.name)
            SetupCfg(package_a.package_name).write(package_a.package_dir)

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "first_commit"])

            package_b = MyPackage(d=self.TMP_DIR, name="packageb")

            os.mkdir(package_b.name)
            SetupCfg(package_b.package_name).write(package_b.package_dir)

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "second_commit"])

            changed_packages = detect_changed_packages.get_changed_packages()
            changed_package = list(changed_packages.keys())

        self.assertEqual(sorted(changed_package), sorted(expected_changes))

    def test_changed_packages_merge_master_detect_changes(self):
        expected_changes = ["company_packaged", "company_packagec"]

        with chdir(self.TMP_DIR):
            subprocess.call(["git", "checkout", "-b", "feature_branch"])

            package_c = MyPackage(d=self.TMP_DIR, name="packagec")

            os.mkdir(package_c.name)
            SetupCfg(package_c.package_name).write(package_c.package_dir)

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "first_commit"])

            package_d = MyPackage(d=self.TMP_DIR, name="packaged")

            os.mkdir(package_d.name)
            SetupCfg(package_d.package_name).write(package_d.package_dir)

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "second_commit"])

            subprocess.call(["git", "checkout", "master"])
            subprocess.call(["git", "merge", "--no-ff", "feature_branch", "-m", "merge to master"])

            # Simulate being on codeship, since we wont be merging locally.
            parent_commit = detect_changed_packages.get_parent_branch()
            os.environ['CI_COMMIT_ID'] = parent_commit

            changed_packages = detect_changed_packages.get_changed_packages()
            changed_package = list(changed_packages.keys())

        self.assertEqual(sorted(changed_package), sorted(expected_changes))

    def test_changed_packages_dependencies(self):
        expected_changes = ["company_package_a", "company_package_b", "company_package_c"]

        with chdir(self.TMP_DIR):
            subprocess.call(["git", "checkout", "-b", "feature_branch"])

            package_a = MyPackage(d=self.TMP_DIR, name="package_a")

            os.mkdir(package_a.name)
            SetupCfg(package_a.package_name).write(package_a.package_dir)

            # package_b depends on package_a
            package_b = MyPackage(d=self.TMP_DIR, name="package_b", local_dependencies=[package_a])
            dependency = [package_b.local_dependencies[0].package_name]
            SetupCfg(package_b.package_name, dependencies=dependency).write(package_b.package_dir)

            # package_c depends on package_b
            package_c = MyPackage(d=self.TMP_DIR, name="package_c", local_dependencies=[package_b])
            dependency = [package_c.local_dependencies[0].package_name]
            SetupCfg(package_c.package_name, dependencies=dependency).write(package_c.package_dir)

            # SHOULD NOT BE DETECTED
            package_d = MyPackage(d=self.TMP_DIR, name="package_d")

            os.mkdir(package_d.name)
            SetupCfg(package_d.package_name).write(package_d.package_dir)

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "commit"])

            subprocess.call(["git", "checkout", "master"])
            subprocess.call(["git", "merge", "--no-ff", "feature_branch", "-m", "merge to master"])

            # New feature branch that changes package_a
            subprocess.call(["git", "checkout", "-b", "feature_branch_2"])

            new_file_path = os.path.join(package_a.package_dir, 'new_module.py')
            with open(new_file_path, 'w') as f:
                f.write('Hello world!\n')

            subprocess.call(["git", "add", "."])
            subprocess.call(["git", "commit", "-m", "commit"])

            all_packages = [package_a, package_b, package_c, package_d]
            changed_packages = detect_changed_packages.get_changed_packages_and_dependents(all_packages)
            changed_package = list(changed_packages.keys())

        self.assertEqual(sorted(changed_package), sorted(expected_changes))

    def test_changed_packages_ignore_changes(self):
        input_changes = [["A", "packagea/README.md"]]
        expected_changes = {}

        with chdir(self.TMP_DIR):
            _dir = "packagea"
            file_name = "README.md"
            File(file_name, "# New readme change!").write(_dir)

            subprocess.call(["git", "add", "."])

            changed_packages = detect_changed_packages.get_unique_changed_packages(input_changes)

        self.assertEqual(changed_packages, expected_changes)

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
