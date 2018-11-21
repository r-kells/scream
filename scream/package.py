import configparser
import logging
import os
import sys


class PackageDoesNotExistException(Exception):
    pass


class CircularDependencyException(Exception):
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
        self.dependencies = self.get_dependents(self.package_dir)
        self.pyversions = self.get_python_versions()
        self.tox_pyversions = self.get_tox_pyversions()

    @staticmethod
    def get_package_dir(package_name):
        """
        Generate the path with a packages source files.
        If package_name is None, try to see if the cwd is a valid package.

        Args:
            package_name (str)
        Returns:
            (str) a path to where the subpackage can be install from.
        """
        cwd = os.getcwd()

        package_name_without_namespace = package_name.split('_')[-1]

        return os.path.join(cwd, package_name_without_namespace)

    def get_dependents(self, package_dir, dependencies=None):
        """ Build local dependencies for a given package.

        Args:
            package (str): a package name to get requirements for.
            dependencies (list): a mutable list to keep track of dependencies in between recursive runs.

        Return:
            (list): the local dependencies required to install the `package` requested.
        """
        if dependencies is None:
            dependencies = []

        requirements = self.get_requirements()

        try:
            for pkg in requirements:
                if pkg == self.package_name:
                    sys.exit("Package {} is dependent on itself!".format(pkg))
                try:
                    package = Package(package_name=pkg)
                except PackageDoesNotExistException:
                    continue
                else:
                    dependencies.append(package)
                    dependencies.extend(package.dependencies)

        except RecursionError:
            sys.exit("Circular dependency detected!")

        return dependencies

    def get_cfg(self, package_dir):
        """
        Parse `setup.cfg` for a given package return a config object to parse further.

        pakages setup is configured in `setup.cfg` rather than setup.py

        Args:
            package_dir (str)

        Returns:
            A config object for the `package`
        """
        config_path = os.path.join(package_dir, 'setup.cfg')
        if not os.path.isfile(config_path):
            logging.debug("`{}` is not a package.".format(package_dir))
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
