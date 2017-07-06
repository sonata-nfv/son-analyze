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
import typing  # noqa pylint: disable=unused-import
import copy
from son_analyze.core import prometheus


def test_prometheus_data_load(basic_query_01, empty_result,
                              error_result) -> None:
    x = prometheus.PrometheusData(basic_query_01)
    assert x.is_success()
    assert len(x.raw['data']['result']) == 1
    assert len(x.raw['data']['result'][0]['values']) == 19
    assert x.raw['data']['result'][0]['metric']['__name__'] == 'cnt_cpu_perc'
    cnt_id = '93a02b23a465d63c3865ed421a437365c464b86e4018f229ee0f91602826b453'
    assert len(x.get_metric_values('cnt_cpu_perc', cnt_id)['values']) == 19
    assert len(x._by_id) == 1
    assert len(x._by_metric_name) == 1
    assert len(x._by_id[cnt_id]) == 1
    assert len(x._by_id[cnt_id][0]['values']) == 19
    v = x._by_id[cnt_id][0]['values'][0]
    assert type(v[1]) == float
    assert 'job' in x.get_metric_values('cnt_cpu_perc', cnt_id)['metric']
    assert 'name' not in x.get_metric_values('cnt_cpu_perc', cnt_id)['metric']
    x = prometheus.PrometheusData(empty_result)
    assert x.is_success()
    assert x.raw['data']['result'] == []
    assert len(x._by_id) == 0
    assert len(x._by_metric_name) == 0
    x = prometheus.PrometheusData(error_result)
    assert not x.is_success()
    assert len(x._by_id) == 0
    assert len(x._by_metric_name) == 0


def test_add_metric_entry(basic_query_01) -> None:
    x = prometheus.PrometheusData(basic_query_01)
    base_entry = x.raw['data']['result'][0]
    new_entry = copy.deepcopy(base_entry)
    new_entry['metric']['__name__'] = 'foobar'
    x.add_entry(new_entry)
    assert len(x.raw['data']['result']) == 2
    assert x.raw['data']['result'][0]['metric']['__name__'] == 'cnt_cpu_perc'
    assert x.raw['data']['result'][1]['metric']['__name__'] == 'foobar'
