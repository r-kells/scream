"""
TODO
githooks
"""
import logging
import os
import subprocess
import sys

from scream.files import Docs, GitIgnore, File, MonorepoReadme, Tox
from scream.utils import WHITELISTED_FILES

INIT_SCREAM_TMPL = "[scream]"
SCREAM_CONFIG_FILE = ".scream"


def init_monorepo(root_dir):
    """
    Args:
        root_dir (str): a path indicating the desired new monorepo location

    Returns:
        Creates dirs and files to initialize a mock new monorepo
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
    Tox().write(root_dir)
    Docs().write(root_dir)

    subprocess.call(["git", "init"])

    logging.info("Done!\nCreate a new package with `scream new <namespace>.<package_name>`")
