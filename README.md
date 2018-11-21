# Scream
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)

What you do when you see a bunch of python... packages.

or...

An opinionated CLI tool for Python monorepo MGMT.

---

It's objective is to ease the creation, testing, and deploying of multiple python packages in a single repository. 
To ensure non-overlapping names with PYPI, this tool forces you to use namespace packages.
Namespaces are defined according to python's [pkgutil-style](https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages).

## Commands

* `scream new <package_name>` - Creates new template package. 
* `scream test [--dry-run][--all]` - Installs a subpackage.
* `scream install <package_name>` - Test subpackages that have changed or who's dependencies have changed since master.
* `scream build` - Run flake8 and tests against all subpackages.

## Highlights

- Creates a consistent blueprint for all packages in a single repository.
    - Code re-use.
    - Consistent Styling.
    - Consistent Testing / Linting / Docs.
- Uses [tox](https://tox.readthedocs.io/en/latest/) to setup virtualenvs for tests.
- Pre-commit hooks to help prevent those gosh darn mistakes.

## Quickstart
```bash
mkdir mymonorepo
cd mymonorepo

scream init

scream new com_packagea
scream new com_packageb

scream test --all

coverage report
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

### Important User Configs
1. In your packages `setup.cfg` the variable `python_requires` 
determines which versions of python your package will be tested against.


## TODO Features

- [ ] Auto version handling.
- [ ] Pre commit hook to flake8.
- [ ] Pre commit hook to avoid committing a large file.
- [ ] Docs builder