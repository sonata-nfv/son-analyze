#! /usr/bin/env python3
"""all.py launch all the tests and checks for this project"""

# pylint: disable=unsubscriptable-object
import sys
import subprocess
import typing  # noqa pylint: disable=unused-import
from typing import List, Tuple
from colorama import init, Fore, Style  # type: ignore


def launch_command(summaries: List[Tuple[str, int]], name: str,
                   command: List[str]) -> None:  # noqa pylint: disable=invalid-sequence-index
    """Start a command and adds its return code in summaries"""
    return_code = subprocess.call(command)
    summaries.append((name, return_code))
    print()


def print_summaries(summaries: List[Tuple[str, int]]) -> None:
    """Print on the console the summaries of the executed commands"""
    def text_summary(name: str, return_code: int) -> str:
        """Returns a colorized string corresponding to the return code"""
        if return_code == 0:
            return '{}  {}: commands succeeded{}'.format(Fore.GREEN,
                                                         name, Style.RESET_ALL)
        else:
            return '{}ERROR, {}: commands failed{}'.format(Fore.RED, name,
                                                           Style.RESET_ALL)
    print('\n{0} summary {0}'.format('_'*35))
    for summary in summaries:
        print(text_summary(*summary))


def main() -> None:
    """Main entrypoint"""
    init()
    args = sys.argv[1:]
    summaries = []  # type: List[Tuple[str, int]]
    commands = [('flake8', 'scripts/flake8.sh'),
                ('pylint', 'scripts/pylint.sh'),
                ('mypy', 'scripts/mypy.sh'),
                ('py.test', 'scripts/py.test.sh'), ]
    for (name, command) in commands:
        launch_command(summaries, name, [command] + args)
    print_summaries(summaries)

if __name__ == '__main__':
    main()
