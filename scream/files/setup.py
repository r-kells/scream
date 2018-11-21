from scream.files.util import File

CFG_TEMPLATE = """\
# Whats this?
# https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files

[metadata]
name = {package_name}
author = example_github_user
email = example_email@gmail.com
version = 0.0.1
description = Your package description!
long_description = file: README.md

[options]
zip_safe = False
packages = find:
python_requires = 2.7, 3.7
# install_requires =
#     example_local_dependency

# dependency_links =
#     git+ssh://git@github.com/example_github_user/example_github_repo.git@master#egg=example-local-dependency-0#subdirectory=example_local_dependency

[options.packages.find]
exclude =
    tests
"""

PY_TEMPLATE = """\
# UPDATE SETTINGS IN setup.cfg.
from setuptools import setup

setup()
"""


class SetupCfg(File):
    def __init__(self, package_name):
        self.package_name = package_name

        super(SetupCfg, self).__init__(
            'setup.cfg',
            CFG_TEMPLATE.format(package_name=self.package_name)
        )


class SetupPy(File):
    def __init__(self):

        super(SetupPy, self).__init__(
            'setup.py',
            PY_TEMPLATE
        )
