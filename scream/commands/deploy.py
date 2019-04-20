import subprocess


def deploy_packages(package_name=None):
    """
    Run a deploy script.
    For packages that have changed (or manually specified by --name=).
    """

    if package_name is None:
        to_deploy = []
        for _, package in to_deploy.items():
            _, package = package.package_name.split('_')
            subprocess.call(["python", "{package}/deploy.py".format(package=package)])
    else:
        subprocess.call(["python", "{package}/deploy.py".format(package=package_name)])
