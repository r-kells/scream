import os
from scream.files.util import File

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
README_DIR = os.path.join(ROOT_DIR, "README.md")

PACKAGE_TEMPLATE = """\
# {title}
![Python <2.7?>](https://img.shields.io/badge/python-<2.7?>-blue.svg)-----

**Table of Contents**

* [Installation](#installation)
* [Tutorial](#tutorial)

## Installation

{package_name} is the best!

## Tutorial
```python
import {package_name}

print("Hello world!")
```
"""

with open(README_DIR) as f:
    MONOREPO_TEMPLATE = f.read()


class PackageReadme(File):
    def __init__(self, package_name):
        super(PackageReadme, self).__init__(
            'README.md',
            PACKAGE_TEMPLATE.format(
                title=package_name,
                package_name=package_name
            )
        )


class MonorepoReadme(File):
    def __init__(self):
        super(MonorepoReadme, self).__init__(
            'README.md',
            MONOREPO_TEMPLATE
        )
