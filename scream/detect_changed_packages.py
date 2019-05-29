import logging
import os
import subprocess

from scream.commands.install import get_dependency_tree
from scream.package import Package, PackageDoesNotExistException

NO_GIT_ERROR_CODE = 128
IGNORE_CHANGES_FILES = ['README.md']

devnull = open(os.devnull, 'w')


class NoGitException(Exception):
    """
    Raised when there is no git repo detected.
    """
    pass


def get_changed_packages_and_dependents(all_packages):
    """A helper function that gets the subpackages that need to be tested or built or deployed.

    Returns:
        (set): a unique set local package names.
    """
    changed_packages = get_changed_packages()

    impacted_packages = {}

    for package_name, package in changed_packages.items():
        impacted_packages.update({package_name: package})

        for package in all_packages:
            dependency_tree = get_dependency_tree(package)
            for dependency in dependency_tree:
                if dependency.package_name in changed_packages.keys():
                    impacted_packages.update({package.package_name: package})

    if impacted_packages:
        logging.info("Packages that require testing / deploying:\n\t{}".format('\n\t'.join(
            list(impacted_packages.keys()))))

    return impacted_packages


def get_changed_packages(verbose=True):
    """Identifies local packages that have changed from HEAD compared to the parent branch.
    Args:
        verbose (bool): controls if we should print logs to console.
    Returns:
        (set): a unique set local package names.
    """
    # subprocess.run("git fetch origin {branch}:origin/{branch}")

    parent_branch = get_parent_branch()
    changed_files = get_changed_files(parent_branch)

    packages_changed = get_unique_changed_packages(changed_files)

    if packages_changed:
        if verbose:
            logging.info(
                "The following packages have changes compared to commit: `{parent_branch}`:\n\t{packages}\n".format(
                    parent_branch=parent_branch,
                    packages='\n\t'.join(list(packages_changed.keys()))
                )
            )
    else:
        logging.info(
            'Either nothing has changed, or there are no valid packages in your current directory.'
        )

    return packages_changed


def parse_git_diff(changed_files):
    files = [f.split('\t') for f in changed_files.splitlines()]
    return files


def get_unique_changed_packages(diffs):
    packages_changed = {}

    for change in diffs:
        if len(change) != 2:
            logging.debug(change)
            continue

        change_type, path = change

        path_tokens = path.split('/')

        # If these files change we should not re-test.
        if path_tokens[-1] in IGNORE_CHANGES_FILES:
            continue

        try:
            package = Package(package_dir=path_tokens[0])
        except PackageDoesNotExistException:
            continue

        # Multiple files could have changed in the same package, but we only want it once.
        if package.package_name not in packages_changed:
            packages_changed.update({package.package_name: package})
    return packages_changed


def get_changed_files(parent_branch):
    try:
        result = subprocess.check_output(
            ["git", "diff", "--name-status", parent_branch],
            stderr=subprocess.STDOUT).decode('utf-8')

    except subprocess.CalledProcessError as err:
        err_out = err.output.decode("utf-8")
        logging.info(err_out)
        return []
    else:
        changed_files = parse_git_diff(result)

    return changed_files


def get_parent_branch():
    # By default its easier to assume we are comparing everything to master.
    # If we can't find a remote master, use local master.
    # Finally, if the CURRENT branch IS master, then check changes since HEAD~1
    parent_branch = "origin/master"

    # Pull in origin/master
    try:
        subprocess.check_call(["git", "fetch", "origin", "master:origin/master"], stderr=devnull)
    except subprocess.CalledProcessError:
        logging.info("No remote master detected, comparing to local master.")

        parent_branch = "master"

    try:
        divergent_commit = subprocess.check_output(["git", "merge-base", "HEAD", parent_branch]) \
            .strip().decode("utf-8")
    except subprocess.CalledProcessError:
        raise NoGitException
    else:
        # Codeship ENV variable to get branch properly.
        ci_commit_id = os.getenv("CI_COMMIT_ID", None)
        if divergent_commit != ci_commit_id:
            return divergent_commit
        else:
            return "HEAD~1"
