#! /usr/bin/env python3
# Copyright (c) 2015 SONATA-NFV, Thales Communications & Security
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, Thales Communications & Security
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).


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
