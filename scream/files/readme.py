import os

from .util import File

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
README_DIR = os.path.join(ROOT_DIR, "README.md")

PACKAGE_TEMPLATE = """\
# {title}
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)-----

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

MONOREPO_TEMPLATE = """\
# Scream
![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

What you do when you see a bunch of python... packages.

or...

An opinionated CLI tool for Python monorepo MGMT.

### Link to all packages [documentation](docs.md)

---

It's objective is to ease the creation, testing, and deploying of multiple python packages in a single repository.
To ensure non-overlapping names with PYPI, this tool forces you to use namespace packages.
Namespaces are defined according to python's
[pkgutil-style](https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages).

- [Scream](#scream)
    - [Why use Scream?](#why-use-scream)
        - [Problems with most monorepos](#problems-with-most-monorepos)
        - [How scream works](#how-scream-works)
    - [Commands](#commands)
    - [Quickstart](#quickstart)
    - [Using your monorepo packages](#using-your-monorepo-packages)
    - [Configuration](#configuration)
    - [Upcoming Features](#upcoming-features)

## Why use Scream?

- Scream holds all packages to the same standards
    - Enforces consistent styling.
    - Enforces consistent testing.
    - Enforces consistent documentation.

- Uses [tox](https://tox.readthedocs.io/en/latest/) to setup virtualenvs for isolated testing across python versions.
- Pre-commit hooks to help prevent those gosh darn mistakes.

### Problems with most monorepos

1. Testing & CI/CD pipeline can become slow with many packages.

    The other available solutions are:
    - Use a build tool like [Pants](https://www.pantsbuild.org/index.html) or [Bazel](https://bazel.build/).

    These tools are extremely powerful, but sometimes are overkill, and introduce a fair amount of overhead to manage.

2. Installing intra-monorepo package dependencies is hard with a private repositories.

    The available solutions are:
    - Have all your packages distributed publically.
    - Host a private PYPI index.
    - pip install using [dependency links](https://python-packaging.readthedocs.io/en/latest/dependencies.html).

### How scream works
Scream aims to cause as little overhead as possible for managing your monorepo.
No fancy third party configuration or private PYPI repositories.

Scream uses the existing python packaging requirements to resolve intra-monorepo dependencies,
and `git` to detect what's changed since the parent branch.

For example:

cat [setup.cfg](https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files).
```ini
[metadata]
name = company_packageA
version = 0.0.1
description = Your package description!

[options]
packages = find:
install_requires =
    company_packageB
```
If you make a change to `company_packageA` then run tests...
```bash
> scream test --dry-run

The following packages have changes compared since branch: `master`:
        company_packagea

Packages that require testing:
        company_packagea
        company_packageb
```

## Commands

* `scream new <package-name>` - Creates new template package.
* `scream test [--dry-run][--all]` - Tests packages and package dependents that have changed.
* `scream install <package-name>` - Installs a package.
* `deploy <package-name>` - Runs deploy.py in your package directory.
* `scream build` - Builds a python wheel and bundles it with all it's dependencies as wheels.

- `-v` will enable verbose logs.

## Quickstart
> By default packages are tested against python 3.7.x, which means you have it available on your PATH.
If you about different versions, please see the [configuration options](#Configuration).

```bash
> mkdir mymonorepo
> cd mymonorepo

> scream init
Done!
Create a new package with `scream new <namespace>.<package_name>`

> scream new com.packagea
Created project `com.packagea`

> scream new com.packageb
Created project `com.packageb`

> scream test --all
Running tests...

> coverage report
```

## Using your monorepo packages
The two common ways you would install packages from this monorepo are:

1. Using `scream build` in your CI tool to build packages and ship them to your machines.
2. Standard pip install individual packages to any machine from private or public github repos.

If your repository is *public*, you can simply install a subpackage anywhere using:
```bash
pip install 'git+ssh://git@github.com/ORG/REPO.git@master#subdirectory=examplea'
```

If your repository is *private*,
you need a few extra steps to make sure packages that depend on other packages in this monorepo can be installed.

1. Specify `dependency_links` in the `setup.cfg` for each 'local' dependency:
```ini
dependency_links =
    git+ssh://git@github.com/ORG/REPO.git@master#egg=examplea-0#subdirectory=subpackages/examplea
```
2. pip install as before, but specifiy the flag `--process-dependency-links`
```bash
pip install 'git+ssh://git@github.com/ORG/REPO.git@master#subdirectory=examplea' --process-dependency-links
```

## Configuration
1. In your packages `setup.cfg` the variable `python_requires`
determines which versions of python your package will be tested against.
- Ex. python_requires = 2.7, 3.6, 3.7
    >  Note: the python versions you intend to test must be available on your path.
"""


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
