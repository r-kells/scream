import subprocess

from scream import detect_changed_packages


def deploy_packages(package_name=None):
    """
    Run a deploy script.
    For packages that have changed (or manually specified by --name=).
    """

    if package_name is None:
        to_deploy = detect_changed_packages.get_changed_packages(verbose=False)
        for _, package in to_deploy.items():
            _, package = package.package_name.split('_')
            subprocess.call(["python", "{package}/deploy.py".format(package=package)])
    else:
        subprocess.call(["python", "{package}/deploy.py".format(package=package_name)])
