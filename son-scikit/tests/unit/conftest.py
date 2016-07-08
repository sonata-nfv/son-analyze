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


# pylint: disable=missing-docstring
import sys
import os
import typing  # noqa pylint: disable=unused-import
from pkg_resources import resource_filename  # type: ignore
import pytest  # type: ignore


def _find_sonanalyze_fixtures() -> str:
    path = os.path.realpath(resource_filename('son_analyze', '../..'))
    return os.path.join(path, 'tests/unit/fixtures')


def _read_static_fixtures_file(relative_path: str,
                               from_sonanalyze=False) -> str:
    """Return the content of a fixture file with the relative path
    `relative_path` from the fixtures directory"""
    base = os.path.join(sys.modules[__name__].__file__, '..', 'fixtures')
    if from_sonanalyze:
        base = _find_sonanalyze_fixtures()
    path = os.path.realpath(os.path.join(base, relative_path))
    with open(path, 'r') as data_file:
        return data_file.read()


@pytest.fixture
def basic_query_01() -> str:
    return _read_static_fixtures_file('basic_query_01.json', True)
