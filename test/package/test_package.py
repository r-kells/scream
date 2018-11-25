try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os

import scream.cli.main as scream
from scream import utils
from scream.package import Package
from test.base_tests import Base


class MockPackage(Package):
    """Override Package constructor so we can test the individual methods.
    """

    def __init__(self):
        pass


class TestChangedPackages(Base.TestNewMonorepoGitInit):

    @classmethod
    def setUp(cls):
        super(TestChangedPackages, cls).setUp()

        cls.package_name = "packagea"
        cls.namespaces = ["company"]
        cls.package_dir = os.path.join(cls.TMP_DIR, cls.package_name)

        with utils.chdir(cls.TMP_DIR):
            # Add a package.
            scream.new_package(
                cls.package_dir,
                namespaces=cls.namespaces,
                package_name=cls.package_name)

    def test_get_configs_bad_dir(self):
        self.assertEqual(MockPackage().get_cfg('tmp'), None)

    def test_get_configs(self):
        self.assertIsInstance(MockPackage().get_cfg(self.package_dir), configparser.ConfigParser)
