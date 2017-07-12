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


"""High level pandas structure for the Sonata prometheus data"""

import datetime
import typing  # noqa pylint: disable=unused-import
from typing import Dict
import pandas  # type: ignore
from son_analyze.core.prometheus import PrometheusData


def convert_timestamp_to_posix(timestamp: str) -> datetime.datetime:
    """Convert the timestamp into a datetime"""
    return datetime.datetime.fromtimestamp(float(timestamp),  # type: ignore
                                           tz=datetime.timezone.utc)


# pylint: disable=unsubscriptable-object
def build_sonata_df_by_id(prom_data: PrometheusData) -> Dict[str,
                                                             pandas.DataFrame]:
    """Build a dict of dataframe. Each dataframe contains the values matching
    the corresponding id"""
    # noqa TODO: find the longest metrics and use it as the index. Interpolate the
    # other metric against it before the merge
    result = {}
    items_itr = prom_data._by_id.items()  # pylint: disable=protected-access
    for id_index, all_metrics in items_itr:
        acc_ts = []
        for elt in all_metrics:
            metric_name = elt['metric']['__name__']
            index, data = zip(*elt['values'])
            index = [convert_timestamp_to_posix(z) for z in index]
            this_serie = pandas.Series(data, index=index)
            this_serie.name = metric_name
            acc_ts.append(this_serie)
        dataframe = pandas.concat(acc_ts, join='outer', axis=1)
        dataframe.index = pandas.date_range(
            start=dataframe.index[0],
            periods=len(dataframe.index),
            freq='S')
        dataframe = dataframe.interpolate(method='index')
        # import pdb; pdb.set_trace()
        result[id_index] = dataframe
    return result
