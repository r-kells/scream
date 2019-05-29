import logging
import subprocess
import sys

from scream.detect_changed_packages import get_changed_packages_and_dependents


def test(all_packages=None, package_name=None, all=False, dry_run=False):
    """Tests all packages that have changed, or packages who's dependencies have changed.
    The tox testing environments can support running package tests against different python versions, etc.
    Args:
        all_packages (list(Package)): all packages, to check for dependency changes
        package_name (str): the name of the package you want to test, including the namespace.
        dry_run (bool): if True, just print what packages have changed, and what packages would be tested.
        all (bool): if True, immediately test all packages (overrides dry-run).

    """
    cmd = build_test_cmd(all_packages, package_name, all, dry_run)
    if cmd:
        result = subprocess.check_call(cmd)
        # Explicitly fail if tests dont succeed, since this call is run in a subprocess.
        if result != 0:
            sys.exit(1)


def build_test_cmd(all_packages=None, package_name=None, all=False, dry_run=False):
    cmd = []

    if package_name is not None:
        logging.info("Testing {}".format(package_name))
        cmd = ["tox", "-e", package_name]
    elif all:
        logging.info("Testing all packages...")
        cmd = ["tox"]

    else:
        if all_packages is None:
            raise Exception(
                "Argument `all_packages` is required to be not None when `package_name` and `all` are not specified.")

        impacted_packages = get_changed_packages_and_dependents(all_packages=all_packages)
        if impacted_packages:

            toxenvs_to_test_list = []

            for _, package in impacted_packages.items():
                for pyversion in package.tox_pyversions:
                    toxenvs_to_test_list.append(pyversion + '-' + package.package_name)

            toxenvs_to_test_str = ','.join(toxenvs_to_test_list)
            cmd = ["tox", "-e", toxenvs_to_test_str]

    if dry_run:
        return

    return cmd
