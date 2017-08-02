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
import os
import logging
import urllib.parse
import typing  # noqa pylint: disable=unused-import
import requests_mock  # type: ignore
from son_analyze.ops import fetch


def test_tmp_workspace_dir(caplog, tmp_workspace_dir: str) -> None:
    caplog.setLevel(logging.DEBUG)
    assert all([
        tmp_workspace_dir,
        os.path.isdir(tmp_workspace_dir),
        os.access(tmp_workspace_dir, os.R_OK),
    ])
    token_path = os.path.join(tmp_workspace_dir, '.son-workspace', 'platforms',
                              'token.txt')
    assert all([
        token_path,
        os.path.isfile(token_path),
        os.access(token_path, os.R_OK),
    ])


def test_fetch_nsd(caplog, tmp_workspace_dir,
                   sonata_demo_mock) -> None:
    caplog.setLevel(logging.DEBUG)
    with requests_mock.Mocker() as mocker:
        for (url, value) in sonata_demo_mock:
            mocker.get(url.geturl(), json=value)
        gate = urllib.parse.urlparse('http://localhost/mock/')
        (nsd, vnfds) = fetch.fetch_nsd(gate, tmp_workspace_dir,
                                       'eu.sonata-nfv.service-descriptor',
                                       'sonata-demo', '0.2.1')
    assert nsd['descriptor_version'] == '1.0'
    assert len(vnfds) == 3
    assert vnfds[0]['descriptor_version'] == 'vnfd-schema-01'


def test_fetch_vnfd_by_uuid(caplog, tmp_workspace_dir,
                            sonata_demo_mock) -> None:
    caplog.setLevel(logging.DEBUG)
    with requests_mock.Mocker() as mocker:
        for (url, value) in sonata_demo_mock:
            mocker.get(url.geturl(), json=value)
        mocker.get('http://localhost/mock/'
                   'functions/c2404aff-cf03-4522-9f9a-80c7d3be6409',
                   status_code=404, text='Not Found')
        gate = urllib.parse.urlparse('http://localhost/mock/')
        vnfd1 = fetch.fetch_vnfd_by_uuid(
            gate, tmp_workspace_dir, 'c2404aff-cf03-4522-9f9a-80c7d3be6409')
        assert not vnfd1
        vnfd2 = fetch.fetch_vnfd_by_uuid(
            gate, tmp_workspace_dir, 'dce50374-c4e2-4902-b6e4-cd23b72e8f19')
        assert len(vnfd2['description']) == 34


def test_fetch_nfd_by_uuid(caplog, tmp_workspace_dir,
                           sonata_demo_mock) -> None:
    caplog.setLevel(logging.DEBUG)
    with requests_mock.Mocker() as mocker:
        for (url, value) in sonata_demo_mock:
            mocker.get(url.geturl(), json=value)
        mocker.get('http://localhost/mock/'
                   'services/c2404aff-cf03-4522-9f9a-80c7d3be6409',
                   status_code=404, text='Not Found')
        gate = urllib.parse.urlparse('http://localhost/mock/')
        nsd1 = fetch.fetch_nsd_by_uuid(
            gate, tmp_workspace_dir, 'c2404aff-cf03-4522-9f9a-80c7d3be6409')
        assert not nsd1
        (nsd2, vnfds2) = fetch.fetch_nsd_by_uuid(
            gate, tmp_workspace_dir, '91460c67-d046-400b-bc34-aadb6514cbfb')
        assert len(nsd2['description']) == 97
        assert len(vnfds2) == 3
        assert vnfds2[1]['name'] == 'iperf-vnf'
