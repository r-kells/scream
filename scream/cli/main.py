# !/usr/bin/env python

import argparse
import logging
import os
import sys

from scream.monorepo import Monorepo
from scream import utils
from scream.commands import install, init_monorepo, new_package, test

NAMESPACE_DELIM = '.'
NAMESPACE_HELP_URL = 'https://github.com/pypa/sample-namespace-packages/tree/master/pkgutil'

INVALID_PACKAGE_NAME_CHARS = ['_']

DESCRIPTION = "An opinionated CLI tool for Python monorepo MGMT."
USAGE = """scream <command> [<args>]

Commands:
* new <package_name>      - Creates new template package.
* test [--dry-run][--all] - Test packages that have changed or who's dependencies have changed since master.
* install <package_name>  - Installs a package.
* build                   - Builds a python wheel and bundles it with all it's dependencies as wheels.
"""

logger = logging.getLogger()
handler = logging.StreamHandler()

formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.setLevel(logging.INFO)


class Scream(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description=DESCRIPTION,
            usage=USAGE
        )

        parser.add_argument('command', help='Subcommand to run')

        # Check if command 'arg' matches one of the class methods.
        # Then use dispatch pattern to invoke method with same name
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logging.info('Unrecognized command')
            parser.print_help()
            exit(1)

        if args.command != 'init':
            try:
                self.monorepo = Monorepo(os.getcwd())
            except FileNotFoundError:
                sys.exit("Slow down partner, run `scream init` in an empty directory first.")

        getattr(self, args.command)()
        # Exit after calling the matching class function
        sys.exit(1)

    # Once we're inside a subcommand, ignore the first
    # TWO argvs, ie the command (scream) and the subcommand (init).
    def init(self):
        help = """Prepares initial setup for the monorepo. """

        argparse.ArgumentParser(description=help)

        init_monorepo(os.getcwd())

    def new(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('package_name')
        args = parser.parse_args(sys.argv[2:])

        # TODO move into Package class
        if NAMESPACE_DELIM not in args.package_name:
            sys.exit("Packages must be namespace packages: <namespace(s)>.<packagename>\n{}".format(
                NAMESPACE_HELP_URL))

        package_name = args.package_name.split(NAMESPACE_DELIM)[-1]
        if any([char in package_name for char in INVALID_PACKAGE_NAME_CHARS]):
            sys.exit("Packages must not contain any of: '{}'".format(','.join(INVALID_PACKAGE_NAME_CHARS)))

        namespaces = args.package_name.split(NAMESPACE_DELIM)[:-1]

        d = os.path.join(self.monorepo.root_dir, package_name)
        if os.path.exists(d):
            logging.info('Directory `{}` already exists.'.format(d))
            sys.exit(1)

        os.makedirs(d)
        with utils.chdir(d, cwd=self.monorepo.root_dir):
            new_package(d, namespaces, package_name, self.monorepo.config)
            logging.info('Created project `{}`'.format(args.package_name))

        self.monorepo.sync()

    def test(self):
        # TODO don't test if simply README changed, etc.
        # self.monorepo.sync()

        parser = argparse.ArgumentParser()
        parser.add_argument('--dry-run', dest='dry_run', default=False, action='store_true')
        parser.add_argument('--all', dest='all', default=False, action='store_true')
        args = parser.parse_args(sys.argv[2:])

        test(dry_run=args.dry_run, all=args.all)

    def install(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('package_name')
        args = parser.parse_args(sys.argv[2:])

        package_name = args.package_name
        install(package_name)
        sys.exit(0)

    # def build(self):
    #     parser = argparse.ArgumentParser(description='help')
    #     parser.add_argument('package_name')
    #     args = parser.parse_args(sys.argv[2:])
    #
    #     raise NotImplementedError(args)


if __name__ == "__main__":
    Scream()
