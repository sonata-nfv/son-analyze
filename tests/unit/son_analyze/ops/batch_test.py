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
import logging
import urllib.parse
import datetime
# from typing import Tuple
import requests_mock  # type: ignore
# import pytest  # type: ignore
from son_analyze.ops import batch


_LOGGER = logging.getLogger(__name__)


def test__create_batches() -> None:
    # pylint: disable=protected-access
    assert not batch._create_batches(10, 0, 1)
    # pylint: disable=protected-access
    assert (batch._create_batches(0, 10, 3) ==
            [(0, 2), (3, 5), (6, 8), (9, 10)])
    tmp = batch._create_batches(1498728359, 1498739158, 5000)
    assert (tmp ==
            [(1498728359, 1498728359 + 4999),
             (1498728359 + 5000, 1498728359 + 9999),
             (1498728359 + 10000, 1498728359 + 10799)])


def test_batch_raw_query(caplog, sonemu_batches_cnt_mem) -> None:
    caplog.setLevel(logging.DEBUG)
    with requests_mock.Mocker() as mocker:
        query = 'container_memory_usage_bytes{name="mn.empty_vnf1"}'
        raw_query = ('container_memory_usage_bytes%7B'
                     'name%3D%22mn.empty_vnf1%22%7D')
        sstamps = [1498728359, 1498728359 + 5000, 1498728359 + 10000]
        estamps = [1498728359 + 4999, 1498728359 + 9999, 1498728359 + 10799]
        for elt in zip(sonemu_batches_cnt_mem, sstamps, estamps):
            url = ('http://localhost/mock/api/v1/query_range'
                   '?start={}&end={}&step={}&query={}').format(
                       elt[1], elt[2], '1s', raw_query
                   )
            mocker.get(url, text=elt[0])
        prom = urllib.parse.urlparse('http://localhost/mock/')
        tmp = batch.batch_raw_query(prom, 1498728359, 1498739158,
                                    datetime.timedelta(seconds=1), query,
                                    5000)
        size = 0
        for rawdata in tmp:
            size += 1
            assert rawdata
        assert size == 3
