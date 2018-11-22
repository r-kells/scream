import os

from contextlib import contextmanager

WHITELISTED_FILES = ['.git', '.idea', '.vscode', '.tox', 'wheelhouse', 'venv']


@contextmanager
def chdir(d, cwd=None):
    origin = cwd or os.getcwd()
    os.chdir(d)

    try:
        yield
    finally:
        os.chdir(origin)
