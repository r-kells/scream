import logging
import os
import subprocess

from scream.package import Package


class NoMatchingDistributionException(Exception):
    pass


def install(package):
    """
    Installs individual subpackages and caches them as wheels in the `wheelhouse` dir.

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

    # develop_cmd = "-f " if develop else ""

    create_wheel_cmd = ["pip", "wheel", "-f", wheelhouse_dir, "-w", wheelhouse_dir, package.package_dir]
    install_cmd = ["pip", "install", "-f", wheelhouse_dir, package.package_name]

    try:
        run(install_cmd)
    except NoMatchingDistributionException:
        run(create_wheel_cmd)
        run(install_cmd)


def run(cmd):
    try:
        r = subprocess.check_output(cmd, stderr=subprocess.PIPE)
        logging.info(r.decode("utf-8"))
    except subprocess.CalledProcessError as err:
        err_str = err.stderr.decode("utf-8")
        if "No matching distribution found" in err_str:
            raise NoMatchingDistributionException(err_str)
