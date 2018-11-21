import logging
import subprocess

from scream.detect_changed_packages import get_changed_packages_and_dependents


def test(dry_run=False, all=False):
    """Tests all subpackages that have changed, or subpackages who's dependencies have changed.
    The tox testing environments can support running package tests against different python versions, etc.
    Args:
        dry_run (bool): if True, just print what packages have changed, and what packages would be tested.
        all (bool): if True, immediately test all packages (overrides dry-run).

    """
    if all:
        logging.info("Testing all packages...")
        subprocess.run(["tox"])
        return

    impacted_packages = get_changed_packages_and_dependents()

    if impacted_packages:
        logging.info("Packages that require testing:\n\t{}".format('\n\t'.join(list(impacted_packages.keys()))))

    if dry_run:
        return

    toxenvs_to_test_list = []

    for _, package in impacted_packages.items():
        for pyversion in package.tox_pyversions:
            toxenvs_to_test_list.append(pyversion + '-' + package.package_name)

    toxenvs_to_test_str = ','.join(toxenvs_to_test_list)

    subprocess.run(["tox", "-e", toxenvs_to_test_str])
