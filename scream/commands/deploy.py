import subprocess
import sys

from scream import detect_changed_packages
from scream.package import Package, PackageDoesNotExistException
from .install import install


def deploy_packages(all_packages=None, package_name=None):
    """
    Run a deploy script.
    For packages that have changed or if your dependencies have changed (or manually specified by --package-name=).
    """

    if package_name is None:
        if all_packages is None:
            raise Exception(
                "Argument `all_packages` is required to be not None when `package_name`is not specified.")

        to_deploy = detect_changed_packages.get_changed_packages_and_dependents(all_packages)
        for _, package in to_deploy.items():

            install(package.package_name)

            _, package = package.package_name.split('_')
            result = subprocess.check_call(["python", "{package}/deploy.py".format(package=package)])

            # Explicitly fail if deploys don't succeed, since this call is run in a subprocess.
            if result != 0:
                sys.exit(1)
    else:
        try:
            package = Package(package_name=package_name)
        except PackageDoesNotExistException:
            raise
        else:
            install(package_name)
            package = package.package_name.split('_')
            result = subprocess.call(["python", "{package}/deploy.py".format(package=package[0])])
        if result != 0:
            sys.exit(1)
