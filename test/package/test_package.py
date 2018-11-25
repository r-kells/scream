try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os

from scream.files.setup import SetupCfg
from scream.package import Package, PackageDoesNotExistException
from scream.utils import chdir
from test.base_tests import Base, MyPackage


class MockPackage(Package):
    """Override Package constructor so we can test the individual methods.
    """

    def __init__(self):
        pass


class TestPackages(Base.TestNewMonorepoGitInit):

    def test_get_configs(self):
        package_a = MyPackage(self.TMP_DIR, "packagea")

        with chdir(self.TMP_DIR):
            os.mkdir(package_a.name)
            SetupCfg(package_a.full_name).write(package_a.package_dir)

            self.assertIsInstance(MockPackage().get_cfg(package_a.package_dir), configparser.ConfigParser)

    def test_get_package_doesnt_exist(self):
        """Test both ways to initialize
        """
        package_a = MyPackage(self.TMP_DIR, "packagea")
        with chdir(self.TMP_DIR):
            with self.assertRaises(PackageDoesNotExistException):
                Package(package_name=package_a.full_name).get_dependents(package_a.package_dir)
            with self.assertRaises(PackageDoesNotExistException):
                Package(package_dir=package_a.package_dir).get_dependents(package_a.package_dir)

    def test_get_package(self):
        package_a = MyPackage(self.TMP_DIR, "packagea")

        SetupCfg(package_a.full_name).write(package_a.package_dir)
        with chdir(self.TMP_DIR):
            Package(package_name=package_a.full_name)
            Package(package_dir=package_a.package_dir)

    def test_resolve_dependencies(self):
        package_c = MyPackage(self.TMP_DIR, "packagec")
        package_b = MyPackage(self.TMP_DIR, "packageb")
        package_a = MyPackage(self.TMP_DIR, "packagea")

        SetupCfg(package_a.full_name, dependencies=[package_b.full_name, package_c.full_name]).write(
            package_a.package_dir)
        SetupCfg(package_b.full_name, dependencies=[package_c.full_name]).write(package_b.package_dir)
        SetupCfg(package_c.full_name).write(package_c.package_dir)

        with chdir(self.TMP_DIR):
            a_dependencies = Package(package_name=package_a.full_name).get_dependents(package_a.package_dir)
            self.assertEqual(a_dependencies[0].package_name, "company_packageb")
            self.assertEqual(a_dependencies[1].package_name, "company_packagec")

    def test_resolve_dependencies_depends_on_itself(self):
        package_a = MyPackage(self.TMP_DIR, "packagea")

        SetupCfg(package_a.full_name, dependencies=[package_a.full_name]).write(package_a.package_dir)

        with chdir(self.TMP_DIR):
            with self.assertRaises(SystemExit) as err:
                Package(package_name=package_a.full_name).get_dependents(package_a.package_dir)
            self.assertTrue('is dependent on itself' in err.exception.args[0])

    def test_resolve_circular_dependencies(self):
        package_b = MyPackage(self.TMP_DIR, "packageb")
        package_a = MyPackage(self.TMP_DIR, "packagea")

        SetupCfg(package_a.full_name, dependencies=[package_b.full_name]).write(package_a.package_dir)
        SetupCfg(package_b.full_name, dependencies=[package_a.full_name]).write(package_b.package_dir)

        with chdir(self.TMP_DIR):
            with self.assertRaises(SystemExit) as err:
                Package(package_name=package_a.full_name).get_dependents(package_a.package_dir)
            self.assertTrue("Circular dependency detected!" in err.exception.args[0])
