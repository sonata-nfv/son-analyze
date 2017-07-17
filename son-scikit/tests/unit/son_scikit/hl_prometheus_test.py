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


# pylint: disable=invalid-name,missing-docstring

import copy
import datetime
import typing  # noqa pylint: disable=unused-import
from son_analyze.core import prometheus
import son_scikit.hl_prometheus as hl


def test_build_sonata_df(basic_query_01):
    x = prometheus.PrometheusData(basic_query_01)
    base_entry = x.raw['data']['result'][0]
    new_entry1 = copy.deepcopy(base_entry)
    new_entry1['metric']['__name__'] = 'uno'
    x.add_entry(new_entry1)
    new_entry2 = copy.deepcopy(base_entry)
    new_entry2['metric']['__name__'] = 'bis'
    new_entry2['values'] = [(i[0], 20+i[1]) for i in new_entry2['values']]
    x.add_entry(new_entry2)
    new_entry3 = copy.deepcopy(base_entry)
    new_entry3['metric']['__name__'] = 'ter'

    def trans(t):  # pylint: disable=missing-docstring,invalid-name
        d = hl.convert_timestamp_to_posix(t[0])
        d = d + datetime.timedelta(0, 1)
        return (d.timestamp(), 30+t[1])

    new_entry3['values'] = [trans(i) for i in new_entry3['values']]
    x.add_entry(new_entry3)
    tmp = hl.build_sonata_df_by_id(x)
    for _, elt in tmp.items():
        assert elt.index.freq == 'S'
        assert any(elt.notnull())
