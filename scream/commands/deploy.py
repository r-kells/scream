import subprocess
import sys

from scream import detect_changed_packages
from scream.package import Package, PackageDoesNotExistException


def deploy_packages(package_name=None):
    """
    Run a deploy script.
    For packages that have changed (or manually specified by --name=).
    """

    if package_name is None:
        to_deploy = detect_changed_packages.get_changed_packages(verbose=False)
        for _, package in to_deploy.items():
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
            package = package.package_name.split('_')
            result = subprocess.call(["python", "{package}/deploy.py".format(package=package[0])])
        if result != 0:
            sys.exit(1)
