import logging
import subprocess
import sys

from scream.package import Package, PackageDoesNotExistException


def get_changed_packages_and_dependents():
    """A helper function that gets the subpackages that need to be tested or built or deployed.

    Returns:
        (set): a unique set local package names.
    """
    changed_packages = get_changed_packages()

    impacted_packages = {}

    for package_name, package in changed_packages.items():

        impacted_packages.update({package_name: package})

        for dependency in package.dependencies:
            impacted_packages.update({dependency.package_name: dependency})

    return impacted_packages


def get_changed_packages():
    """Identifies local packages that have changed from HEAD compared to the parent branch.

    Returns:
        (set): a unique set local package names.
    """
    parent_branch = subprocess.check_output("detect_parent_branch.sh").decode('utf-8')
    if parent_branch == '':
        # You are probably on master...
        parent_branch = 'master'
    # subprocess.run("git fetch origin {branch}:origin/{branch}")
    try:
        result = subprocess.check_output(["git", "diff", "--name-status", parent_branch],
                                         stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as err:
        if 'Not a git repository' in err.output.decode('utf-8'):
            sys.exit("No git repository detected. Scream uses git to determine "
                     "what packages have changed and require tests.")
        else:
            logging.info(err.cmd)
            sys.exit('Unknown git error: {}'.format(err.output.decode('utf-8')))

    diffs = [diff.split('\t') for diff in result.splitlines()]

    packages_changed = {}

    for change in diffs:
        if len(change) != 2:
            continue

        change_type, path = change
        try:
            package = Package(package_dir=path.split('/')[0])
        except PackageDoesNotExistException:
            continue

        # Multiple files could have changed in the same package, but we only want it once.
        if package.package_name not in packages_changed:
            packages_changed.update({package.package_name: package})

    if packages_changed:
        logging.info(
            "The following packages have changes compared since branch: `{parent_branch}`:\n\t{packages}\n".format(
                parent_branch=parent_branch,
                packages='\n\t'.join(list(packages_changed.keys()))))
    else:
        logging.info('Either nothing has changed, or there are no valid packages in your current directory.')

    return packages_changed
