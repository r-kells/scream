try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os
import sys

NAMESPACE_DELIM = '.'
NAMESPACE_HELP_URL = 'https://github.com/pypa/sample-namespace-packages/tree/master/pkgutil'
INVALID_PACKAGE_NAME_CHARS = ['_']


class PackageDoesNotExistException(Exception):
    pass


class PackageNamingException(Exception):
    pass


class Package:
    def __init__(self, package_name=None, package_dir=None):
        self.package_dir = package_dir or self.get_package_dir(package_name)

        # If package_dir doesnt have a `setup.cfg` it is not a valid package.
        self.config = self.get_cfg(self.package_dir)
        if self.config is None:
            raise PackageDoesNotExistException("No valid package found in {}".format(self.package_dir))

        # Expose relevant package variables here...
        self.package_name = package_name or self.get_package_name()
        self.local_dependencies, self.other_dependencies = self.get_dependents(self.package_dir)
        self.pyversions = self.get_python_versions()
        self.tox_pyversions = self.get_tox_pyversions()

    @staticmethod
    def get_package_dir(package_name):
        """
        Generate the path with a packages source files.

        Args:
            package_name (str)
        Returns:
            (str) a path to where the subpackage can be install from.
        """
        cwd = os.getcwd()

        package_name_without_namespace = package_name.split('_')[-1]

        return os.path.join(cwd, package_name_without_namespace)

    def get_dependents(self, package_dir, local_dependencies=None, other_dependencies=None):
        """ Build local dependencies for a given package.

        Args:
            package_dir (str): a dir containing a package to get requirements for.
            local_dependencies (list): keeps track of mono repo dependencies in between recursive runs.
            other_dependencies (list): keeps track of other (pypi) dependencies in between recursive runs.

        Return:
            (list): the local dependencies required to install the `package` requested.
        """
        if local_dependencies is None:
            local_dependencies = []
        if other_dependencies is None:
            other_dependencies = []

        requirements = self.get_requirements()
        try:
            for pkg in requirements:
                if pkg == self.package_name:
                    sys.exit("Package {} is dependent on itself!".format(pkg))
                try:
                    package = Package(package_name=pkg)
                except PackageDoesNotExistException:
                    other_dependencies.append(pkg)
                else:
                    local_dependencies.append(package)
                    local_dependencies.extend(package.local_dependencies)
                    other_dependencies.extend(package.other_dependencies)

        except RuntimeError:
            sys.exit("Circular dependency detected!")

        return local_dependencies, other_dependencies

    def get_cfg(self, package_dir):
        """
        Parse `setup.cfg` for a given package return a config object to parse further.

        packages setup is configured in `setup.cfg` rather than setup.py

        Args:
            package_dir (str)

        Returns:
            A config object for the `package`
        """
        config_path = os.path.join(package_dir, 'setup.cfg')
        if not os.path.isfile(config_path):
            return None

        config = configparser.ConfigParser()
        config.read(config_path)

        return config

    def get_package_name(self):
        return self.config['metadata'].get('name')

    def get_requirements(self):
        return self.config['options'].get('install_requires', '').split('\n')[1:]

    def get_python_versions(self):
        version_str = self.config['options'].get('python_requires')
        return [v.strip() for v in version_str.split(',')]

    def get_tox_pyversions(self):
        versions = self.get_python_versions()
        return ["py{}".format(v.replace('.', '')) for v in versions]


def validate_package_name(name):
    if NAMESPACE_DELIM not in name:
        raise PackageNamingException(
            "Packages must be namespace packages: <namespace(s)>.<packagename>\n{}".format(
                NAMESPACE_HELP_URL))

    package_name = name.split(NAMESPACE_DELIM)[-1]
    if any([char in package_name for char in INVALID_PACKAGE_NAME_CHARS]):
        sys.exit("Packages must not contain any of: '{}'".format(','.join(INVALID_PACKAGE_NAME_CHARS)))

    tokens = name.split(NAMESPACE_DELIM)
    namespaces = tokens[:-1]
    package_name = tokens[-1]

    return namespaces, package_name
