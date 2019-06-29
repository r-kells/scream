import unittest

import mock

from scream.monorepo import Monorepo, version_counter
from scream.package import Package


class MockPackage(Package):
    """Override Package constructor so we can test the individual methods.
    """

    def __init__(self):
        pass


class MockScream():
    def __init__(self, packages):
        self.packages = packages


class TestPackages(unittest.TestCase):
    package_1 = MockPackage()
    package_1.package_name = 'package_1'
    package_1.other_dependencies = ['wheel', 'wheel==1.1', 'requests==1.2']

    package_2 = MockPackage()
    package_2.package_name = 'package_2'
    package_2.other_dependencies = ['wheel', 'wheel==1.2', 'requests==1.2']

    s = MockScream([package_1, package_2])

    def test_simple_none(self):
        with mock.patch.object(Monorepo, "__init__", lambda x, y: None):
            repo = Monorepo(None)
            repo.config = self.s

            repo.validate_mono_repo()

    def test_warn_unpinned_packages(self):
        pypi_packages = ['flask', 'flask==1.2.3']
        with mock.patch.object(Monorepo, "__init__", lambda x, y: None):
            repo = Monorepo(None)
            actual = repo.warn_unpinned_packages(pypi_packages)
            expected = ['flask']
            self.assertEqual(expected, actual)

    def test_warn_dependency_conflict(self):
        tests = [
            {
                "name": "different_versions",
                "data": ['flask', 'flask==1.0', 'flask==2.0', 'other==1.0'],
                "want": ['flask', 'flask==1.0', 'flask==2.0']
            },
            {
                "name": "same_version_with_unversioned",
                "data": ['flask', 'flask==1.2.3', 'flask==1.2.3', 'other=1.0'],
                "want": ['flask', 'flask==1.2.3', 'flask==1.2.3']
            },
            {
                "name": "all_diff_versions",
                "data": ['flask==1.0', 'flask==2.0', 'flask==3.0', 'other=1.0'],
                "want": ['flask==1.0', 'flask==2.0', 'flask==3.0']
            },
            {
                "name": "two_no_versions",
                "data": ['flask', 'flask', 'other=1.0'],
                "want": []
            }
        ]
        with mock.patch.object(Monorepo, "__init__", lambda x, y: None):
            repo = Monorepo(None)

            for test in tests:
                actual = repo.warn_dependency_conflict(test['data'])
                self.assertEqual(test['want'], actual, msg=test['name'])

    def test_version_counter(self):
        pypi_packages = ['flask', 'flask==1.0', 'other==1.0']

        actual = version_counter(pypi_packages)
        expected = {"flask": set(["1.0", "LATEST"]), "other": set(["1.0"])}
        self.assertEqual(expected, actual)
