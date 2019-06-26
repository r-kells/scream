import unittest

import mock

from scream.monorepo import Monorepo
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
    package_1.other_dependencies = ['flask', 'wheel==1.1', 'requests==1.2']

    package_2 = MockPackage()
    package_2.package_name = 'package_2'
    package_2.other_dependencies = ['flask', 'wheel==1.2', 'requests==1.2']

    s = MockScream([package_1, package_2])

    # TODO: individual method tests.
    def test_simple_none(self):
        with mock.patch.object(Monorepo, "__init__", lambda x, y: None):
            repo = Monorepo(None)
            repo.config = self.s

            repo.validate_mono_repo()
