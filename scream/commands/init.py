"""
TODO
init creates gitnignore, hooks, and special 'scream' file to indicate the root dir
scream file also maintains list of packages? s
scream can be a list of user settings.
update tox file with new packages when they are added so testing is seamless
"""
import logging
import os
import sys

from scream.files import GitIgnore, File, MonorepoReadme, Tox
from scream.utils import WHITELISTED_FILES

INIT_SCREAM_TMPL = "[scream]"
SCREAM_CONFIG_FILE = ".scream"


def init_monorepo(root_dir):
    """
    \b
    ├── example_pkg_a/
    ├── example_pkg_b/
    ├── example_pkg_c/
    ├── .scream
    ├── README.md
    └── tox.ini
    """
    # Can only initialize an empty directory, just to make sure you don't screw it up.
    files = os.listdir(root_dir)

    for f in WHITELISTED_FILES:
        if f in files:
            files.remove(f)

    if files:
        sys.exit("You must start a mono repo in an empty dir. This is for your own safety.")

    File(SCREAM_CONFIG_FILE, INIT_SCREAM_TMPL).write(root_dir)

    MonorepoReadme().write(root_dir)
    GitIgnore().write(root_dir)
    Tox(packages=[]).write(root_dir)

    logging.info("Done! Create a new package with `scream new <namespace>.<package_name>`")
