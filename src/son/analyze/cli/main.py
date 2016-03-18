"""son-analyze command line tool"""

import sys
import argparse
from argparse import Namespace
import typing  # noqa pylint: disable=unused-import
from typing import List
from son.analyze import __version__


def version(args: Namespace) -> None:
    """Print the current version and exit"""
    msg = 'son-analyze version: {}'.format(__version__)
    if args.short:
        msg = __version__
    print(msg)
    sys.exit(0)


def dummy(_: Namespace) -> None:
    """Do something dummy and exit"""
    print('Dummy')
    sys.exit(1)


def dispatch(raw_args: List) -> None:
    """Parse the raw_args and dispatch the control flow"""
    parser = argparse.ArgumentParser(description=('An analysis framework '
                                                  'creation tool for Sonata'))
    parser.add_argument('-v', '--verbose', type=int, default=0,
                        help='increase verbosity')

    def no_command(_: Namespace) -> None:
        """Print the help usage and exit"""
        parser.print_help()
        sys.exit(0)
    parser.set_defaults(func=no_command)
    subparsers = parser.add_subparsers()

    parser_version = subparsers.add_parser('version', help='Show the version')
    parser_version.add_argument('--short', default=False, action='store_true',
                                help='Shows only the version')
    parser_version.set_defaults(func=version)

    parser_dummy = subparsers.add_parser('dummy', help='Do something dummy')
    parser_dummy.set_defaults(func=dummy)

    args = parser.parse_args(raw_args)
    args.func(args)
    assert False  # this line is impossible to reach


def main() -> None:
    """Main entry point for the son-analyze command line tool"""
    dispatch(sys.argv[1:])
