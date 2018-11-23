from .util import File

TEMPLATE = """\
build/
.cache/
.coverage
.python-version
dist/
docs/build/
.DS_Store
.idea/
*.egg-info/
*.log
*.pyc
.tox/
venv/
.vscode/
wheelhouse/
"""


class GitIgnore(File):
    def __init__(self):
        super(GitIgnore, self).__init__(
            '.gitignore',
            TEMPLATE
        )
