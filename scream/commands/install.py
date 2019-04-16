import logging
import os
import subprocess

from scream.detect_changed_packages import get_changed_packages
from ..package import Package


class NoMatchingDistributionException(Exception):
    pass


class PackageInstallationException(Exception):
    pass


def install(package):
    """
    Installs individual packages and their dependents then caches them as wheels in the `wheelhouse` dir.

    Args:
        package (str): A local package name. Ex: `company_examplea`.

    """
    changed_packages = get_changed_packages(verbose=False)

    package = Package(package_name=package)
    logging.info("Installing package: `{}`...".format(package.package_name))

    for dependent_package in package.local_dependencies:
        logging.info("Installing dependency: `{}`...".format(dependent_package.package_name))
        _install_package(dependent_package, changed_packages)

    # finally install the package that was originally requested.
    _install_package(package)

    logging.info("Installation complete.")


def _install_package(package, changed_packages=None):
    """
    Tries to install `package` from the wheelhouse cache.
    If it doesnt exist:
        1. Create the wheel, so future packages can skip the work.
        2. Install from the wheelhouse.

    Args:
        package (str): a package name to install
        changed_packages (list[Package]) Since we might have changed multiple packages in this commit
            re-build wheels for all changed package dependencies.
    """
    if changed_packages is None:
        changed_packages = []

    wheelhouse_dir = os.path.join(os.path.dirname(package.package_dir), "wheelhouse")

    create_wheel_cmd = ["pip", "wheel", "-f", wheelhouse_dir, "-w", wheelhouse_dir, package.package_dir]
    install_cmd = ["pip", "install", "-f", wheelhouse_dir]

    for other_deps in package.other_dependencies:
        run(install_cmd + [other_deps])
    try:
        if package.package_name in changed_packages:
            logging.info("Package {} has changed, rebuilding wheel.".format(package.package_name))
            run(create_wheel_cmd)

        run(install_cmd + [package.package_name])
    except NoMatchingDistributionException:
        run(create_wheel_cmd)
        run(install_cmd + [package.package_name])


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
