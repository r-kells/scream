import logging
import os
import subprocess

from ..package import Package


class NoMatchingDistributionException(Exception):
    pass


def install(package):
    """
    Installs individual packages and their dependents then caches them as wheels in the `wheelhouse` dir.

    Args:
        package (str): A local package name. Ex: `company_examplea`.

    """
    package = Package(package_name=package)
    logging.info("Installing package: `{}`...".format(package.package_name))

    # Before checking dependencies, see if we can install straight away.
    try:
        _install_package(package)
    except NoMatchingDistributionException:

        for dependent_package in package.dependencies:
            _install_package(dependent_package)

        # finally install the package that was originally requested.
        _install_package(package)

    logging.info("Installation complete.")


def _install_package(package):
    """
    Tries to install `package` from the wheelhouse cache.
    If it doesnt exist:
        1. Create the wheel, so future packages can skip the work.
        2. Install from the wheelhouse.

    Args:
        package (str): a package name to install
    """
    wheelhouse_dir = os.path.join(os.path.dirname(package.package_dir), "wheelhouse")

    create_wheel_cmd = ["pip", "wheel", "-f", wheelhouse_dir, "-w", wheelhouse_dir, package.package_dir]
    install_cmd = ["pip", "install", "-f", wheelhouse_dir, package.package_name]

    try:
        run(install_cmd)
    except NoMatchingDistributionException:
        run(create_wheel_cmd)
        run(install_cmd)


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
