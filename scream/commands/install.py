import logging
import subprocess

from ..package import Package


class NoMatchingDistributionException(Exception):
    pass


class PackageInstallationException(Exception):
    pass


def install(package):
    """
    Installs individual packages and their dependents.

    Args:
        package (str): A local package name. Ex: `company_examplea`.

    """
    package = Package(package_name=package)
    logging.info("Installing package: `{}`...".format(package.package_name))

    # Try to install package directly, if fails install dependencies first.
    try:
        _install_package(package)
        return
    except NoMatchingDistributionException:
        # Must need to install dependencies first.
        pass

    dependency_tree = get_dependency_tree(package)

    for p in dependency_tree:
        logging.info("Installing {}.".format(p.package_name))
        _install_package(p)

    # finally install the package that was originally requested.
    _install_package(package)

    logging.info("Installation complete.")


def _install_package(package):
    """
    Tries to install `package` from local dir.

    Args:
        package (str): a package name to install
    """
    run(["pip", "install", "-e", package.package_dir])


def run(cmd):
    """A helper to run and catch installation errors.
    Args:
        cmd (list): a set of commands to run in the shell.

    Returns:
        Executes the `cmd`
    Raises:
        NoMatchingDistributionException
    """
    try:
        r = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        logging.info(r.decode("utf-8"))
    except subprocess.CalledProcessError as err:
        err_str = err.output.decode("utf-8")
        if "No matching distribution found" in err_str:
            raise NoMatchingDistributionException(err_str)
        raise PackageInstallationException(err_str)


# TODO move to package.py
def get_dependency_tree(package, dependency_tree=None):
    """Recursively fetch depth first dependency tree of local packages.

    Return list(Package):
        A reversed dependency tree: the order to install packages.
    """
    if dependency_tree is None:
        dependency_tree = []

    for dependent_package in package.local_dependencies:
        dependency_tree.append(dependent_package)
        get_dependency_tree(dependent_package, dependency_tree=dependency_tree)
    return reversed(dependency_tree)
