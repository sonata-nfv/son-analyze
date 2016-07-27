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


# noqa pylint: disable=unsubscriptable-object,missing-docstring,redefined-outer-name,invalid-sequence-index
import sys
import os
import logging
from urllib.parse import ParseResult, urlparse
from typing import Dict, Any, List, Tuple
import yaml  # type: ignore
import pytest  # type: ignore


_LOGGER = logging.getLogger(__name__)


def _read_static_fixtures_file(relative_path: str) -> str:
    """Return the content of a fixture file with the relative path
    `relative_path` from the fixtures directory"""
    path = os.path.realpath(os.path.join(sys.modules[__name__].__file__,
                                         '..', 'fixtures',
                                         relative_path))
    with open(path, 'r') as data_file:
        return data_file.read()


@pytest.fixture
def basic_query_01() -> str:
    return _read_static_fixtures_file('basic_query_01.json')


@pytest.fixture
def empty_result() -> str:
    return _read_static_fixtures_file('empty_result.json')


@pytest.fixture
def error_result() -> str:
    return _read_static_fixtures_file('error_result.json')


@pytest.fixture
def sonata_demo_nsd_91460c67() -> Tuple[str, str]:
    return ('91460c67-d046-400b-bc34-aadb6514cbfb',
            _read_static_fixtures_file('sonata-demo-nsd.91460c67-d046'
                                       '-400b-bc34-aadb6514cbfb.yml'))


@pytest.fixture
def iperf_vnfd_d0ac3202() -> Tuple[str, str]:
    return ('d0ac3202-3f1c-412d-b7a8-6d9d0034ec45',
            _read_static_fixtures_file('iperf-vnfd.d0ac3202-3f1c'
                                       '-412d-b7a8-6d9d0034ec45.yml'))


@pytest.fixture
def firewall_vnfd_dce50374() -> Tuple[str, str]:
    return ('dce50374-c4e2-4902-b6e4-cd23b72e8f19',
            _read_static_fixtures_file('firewall-vnfd.dce50374-c4e2'
                                       '-4902-b6e4-cd23b72e8f19.yml'))


@pytest.fixture
def tcpdump_vnfd_18741f2a() -> Tuple[str, str]:
    return ('18741f2a-a8d5-4de2-a3bf-3608bd30d281',
            _read_static_fixtures_file('tcpdump-vnfd.18741f2a-a8d5'
                                       '-4de2-a3bf-3608bd30d281.yml'))


@pytest.fixture
def sonata_demo_mock(
        sonata_demo_nsd_91460c67,
        iperf_vnfd_d0ac3202,
        firewall_vnfd_dce50374,
        tcpdump_vnfd_18741f2a) -> List[Tuple[ParseResult,
                                             List[Dict[str, List[Any]]]]]:
    files = [
        ('services', sonata_demo_nsd_91460c67[0],
         yaml.load(sonata_demo_nsd_91460c67[1])),
        ('functions', iperf_vnfd_d0ac3202[0],
         yaml.load(iperf_vnfd_d0ac3202[1])),
        ('functions', firewall_vnfd_dce50374[0],
         yaml.load(firewall_vnfd_dce50374[1])),
        ('functions', tcpdump_vnfd_18741f2a[0],
         yaml.load(tcpdump_vnfd_18741f2a[1]))
    ]

    def compute_urls(path, uuid, val):  # pylint: disable=missing-docstring
        base = 'http://localhost/mock'
        url1 = ('{:s}/{:s}?name={:s}&vendor={:s}&version={:s}').format(
            base, path, val['name'], val['vendor'], val['version'])
        url2 = ('{:s}/{:s}/{:s}'.format(base, path, uuid))
        return (urlparse(url1), urlparse(url2))

    result = []
    for elt in files:
        urls = compute_urls(elt[0], elt[1], elt[2])
        result.append((urls[0], [elt[2]]))
        result.append((urls[1], elt[2]))
    _LOGGER.debug([elt[0].geturl() for elt in result])
    return result


@pytest.fixture
def firewall_vnfr_9b4663bc() -> str:
    return _read_static_fixtures_file('firewall-vnfr.9b4663bc-d7af'
                                      '-40bf-8efe-3dc069b2349f.yml')


@pytest.fixture
def iperf_vnfr_0896785c() -> str:
    return _read_static_fixtures_file('iperf-vnfr.0896785c-4d6e-4b7f'
                                      '-acff-44f3b927fa86.yml')


@pytest.fixture
def tcpdump_vnfr_6b64cc54() -> str:
    return _read_static_fixtures_file('tcpdump-vnfr.6b64cc54-83a7'
                                      '-4172-9f5f-98b93c5c3a4e.yml')


@pytest.fixture
def sonata_demo_nsr_0295d535() -> str:
    return _read_static_fixtures_file('sonata-demo-nsr.0295d535-208e'
                                      '-4a5d-abc6-ca0e06b44d8e.yml')


@pytest.fixture
def sonata_demo_nsr_mock(
        sonata_demo_nsr_0295d535,
        iperf_vnfr_0896785c,
        firewall_vnfr_9b4663bc,
        tcpdump_vnfr_6b64cc54) -> List[Tuple[ParseResult,
                                             List[Dict[str, List[Any]]]]]:
    files = [
        ('records/nsr', yaml.load(sonata_demo_nsr_0295d535)),
        ('records/vnfr', yaml.load(iperf_vnfr_0896785c)),
        ('records/vnfr', yaml.load(firewall_vnfr_9b4663bc)),
        ('records/vnfr', yaml.load(tcpdump_vnfr_6b64cc54))
    ]

    def compute_url(path, val):  # pylint: disable=missing-docstring
        base = ('http://localhost/mock/{:s}/{:s}').format(
            path, val['id'])
        return urlparse(base)

    return [(compute_url(elt[0], elt[1]), [elt[1]]) for elt in files]
