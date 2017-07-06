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


"""functions related to prometheus"""

import json
from typing import Any, Dict, Callable


class PrometheusData:
    """
    The PrometheusData object contains the raw data for a Prometheus
    query
    """

    def __init__(self, raw_json: str) -> None:
        """Constructor from a string containing a json structure"""
        self.raw = json.loads(raw_json)  # Dict[Any, Any]
        self._rectify_types()
        self._by_id = {}  # type: Dict[str, Any]
        self._by_metric_name = {}  # type: Dict[str, Any]
        self._build_indexes()

    def _rectify_types(self) -> None:
        """Iterate over the initial data to change to type of some data from
        str to something else: float, ..."""
        if not self.is_success():
            return
        table = {
            'cnt_cpu_perc': float,
            'sonemu_rx_count_packets': float,
            'container_memory_usage_bytes': int
        }  # type: Dict[str, Callable[[Any], Any]]

        def get_conv(key: str) -> Callable[[Any], Any]:
            """return a function to convert a value based on the key"""
            return table.get(key, str)
        conv = None
        for elt in self.raw['data']['result']:
            conv = get_conv(elt['metric']['__name__'])
            # conv = table.get(elt['metric']['__name__'], str)
            elt['values'] = [(val[0], conv(val[1])) for val in elt['values']]

    def _build_indexes(self) -> None:
        """Create some indexes to provide some search shortcuts over data"""
        self._by_id = {}
        self._by_metric_name = {}
        if not self.is_success():
            return
        for elt in self.raw['data']['result']:
            elt_id = elt['metric']['id']
            to_update_by_id = self._by_id.get(elt_id, [])
            to_update_by_id.append(elt)
            self._by_id[elt_id] = to_update_by_id
            elt_name = elt['metric']['__name__']
            to_update_by_name = self._by_metric_name.get(elt_name, {})
            to_update_by_name[elt_id] = elt
            self._by_metric_name[elt_name] = to_update_by_name

    def is_success(self):
        """Test if the related data is a success or an error
        Returns `True` in case of a success, `False` otherwise
        """
        return self.raw["status"] == 'success'

    def get_metric_values(self, metric_name: str, target_id: str) -> Any:
        """Return the `metric_name` metric values corresponding to the
        `target_id` id component"""
        results = self.raw["data"]["result"]

        def somefilter(result):
            """Filter result and return elements containing the targeted
            `metric_name` and `target_id` fields"""
            tmp = result['metric']
            return tmp['__name__'] == metric_name and tmp['id'] == target_id

        targets = [tmp for tmp in results if somefilter(tmp)]
        if len(targets) == 1:
            return targets[0]
        return None

    # pylint: disable=unsubscriptable-object
    def add_entry(self, metric: Dict[str, Any]) -> None:
        """Add a new metric"""
        possible_collision = self.get_metric_values(
            metric['metric']['__name__'],
            metric['metric']['id'])
        if possible_collision:
            possible_collision['values'] += metric['values']
        else:
            self.raw['data']['result'].append(metric)
            self._build_indexes()
