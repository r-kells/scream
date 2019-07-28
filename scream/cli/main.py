# !/usr/bin/env python

import argparse
import logging
import os
import sys

from scream import utils
from scream.commands import deploy_packages, install, init_monorepo, new_package, test, PackageInstallationException
from scream.monorepo import Monorepo
from scream.package import PackageDoesNotExistException, PackageNamingException, validate_package_name

DESCRIPTION = "An opinionated CLI tool for Python monorepo MGMT."
USAGE = """scream <command> [<args>] [-v]

Commands:
    init                    - Run this first. Initiates a monorepo in an empty directory.
    new <package-name>      - Creates new template package.
    test [--dry-run][--all] - Test packages that have changed or who's dependencies have changed since master.
    install <package-name>  - Installs a package.
    deploy <package-name>   - Runs deploy.py in your package directory.
    build                   - Builds a python wheel and bundles it with all it's dependencies as wheels.
"""


class CustomFormatter(logging.Formatter):
    """Logging Formatter configure a different format for INFO vs. other log levels.
    INFO formatting is used for communicating informative messages to the user.
    """

    FORMATS = {
        logging.INFO: "%(msg)s",
        "DEFAULT": "%(levelname)s: %(msg)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


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
            except IOError:
                logging.error("Slow down partner, run `scream init` in an empty directory first.")
                sys.exit(1)

        getattr(self, args.command)()
        # Exit after calling the matching class function
        sys.exit(0)

    # Once we're inside a subcommand, ignore the first
    # TWO argvs, ie the command (scream) and the subcommand (init).
    def init(self):
        help = """Prepares initial setup for the monorepo. """

        argparse.ArgumentParser(description=help)

        init_monorepo(os.getcwd())

    def new(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", action='store_true', help="enable debug logging")
        parser.add_argument('package_name', help="a <namespace>.<packagename> is required.")

        args = parser.parse_args(sys.argv[2:])
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        try:
            namespaces, package_name = validate_package_name(args.package_name)
        except PackageNamingException as err:
            sys.exit(err)

        d = os.path.join(self.monorepo.root_dir, package_name)
        if os.path.exists(d):
            logging.info('Directory `{}` already exists.'.format(d))
            sys.exit(1)

        os.makedirs(d)
        with utils.chdir(d, cwd=self.monorepo.root_dir):
            new_package(d, namespaces, package_name)
            logging.info('Created project `{}`'.format(args.package_name))

        self.monorepo.sync()

    def test(self):
        help = "Tests packages that have changed compared to the parent branch."
        self.monorepo.sync()

        parser = argparse.ArgumentParser(description=help)
        parser.add_argument("-v", "--verbose", action='store_true', help="enable debug logging")
        parser.add_argument('--package-name', dest='package_name',
                            help="Test this package, regardless of git status.")
        parser.add_argument('--dry-run', dest='dry_run', default=False, action='store_true',
                            help="Print what would be tested, but don't run tests.")
        parser.add_argument('--all', dest='all', default=False, action='store_true',
                            help="Test all packages, ragardless of git status.")

        args = parser.parse_args(sys.argv[2:])
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        test(all_packages=self.monorepo.config.packages, package_name=args.package_name, dry_run=args.dry_run,
             all=args.all)

        self.monorepo.validate_mono_repo()

    def install(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", action='store_true', help="enable debug logging")
        parser.add_argument('package_name')

        args = parser.parse_args(sys.argv[2:])
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        try:
            install(args.package_name)
        except PackageDoesNotExistException:
            logging.error("Package doesn't exit. Packages are named '<namespace(s)>_<name>'")
            sys.exit(1)
        except PackageInstallationException as e:
            logging.error(e)
            sys.exit(1)

    def build(self):
        help = "WARNING: NOT IMPLIMENTED - Build a versioned zip that contains the package " \
               "and a directory of it's versioned dependencies."
        parser = argparse.ArgumentParser(description=help)
        parser.add_argument("-v", "--verbose", action='store_true', help="enable debug logging")
        parser.add_argument('--package-name', dest='package_name')

        args = parser.parse_args(sys.argv[2:])
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        raise NotImplementedError(args)

    def deploy(self):
        """
        Run a deploy script.
        For packages that have changed (or manually specified by --package-name <mypackage>).
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", action='store_true', help="enable debug logging")
        parser.add_argument('--package-name', dest='package_name')

        args = parser.parse_args(sys.argv[2:])
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        if args.package_name is None:
            deploy_packages(all_packages=self.monorepo.config.packages)

        else:
            try:
                deploy_packages(package_name=args.package_name)
            except PackageDoesNotExistException:
                logging.info("That package does not exist!")


if __name__ == "__main__":
    Scream()
