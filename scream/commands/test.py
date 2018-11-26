import logging
import subprocess

from scream.detect_changed_packages import get_changed_packages_and_dependents


def test(package_name=None, all=False, dry_run=False):
    """Tests all packages that have changed, or packages who's dependencies have changed.
    The tox testing environments can support running package tests against different python versions, etc.
    Args:
        package_name (str): the name of the package you want to test, including the namespace.
        dry_run (bool): if True, just print what packages have changed, and what packages would be tested.
        all (bool): if True, immediately test all packages (overrides dry-run).

    """
    cmd = build_test_cmd(package_name, all, dry_run)
    if cmd:
        subprocess.call(cmd)


def build_test_cmd(package_name=None, all=False, dry_run=False):
    cmd = []

    if package_name is not None:
        logging.info("Testing {}".format(package_name))
        cmd = ["tox", "-e", package_name]
    elif all:
        logging.info("Testing all packages...")
        cmd = ["tox"]

    else:
        impacted_packages = get_changed_packages_and_dependents()
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
