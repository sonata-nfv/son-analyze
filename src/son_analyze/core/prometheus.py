"""functions related to prometheus"""

from typing import Any
import json


class PrometheusData:
    """
    The PrometheusData object contains the raw data for a Prometheus
    query
    """

    def __init__(self, raw_json: str) -> None:
        """Constructor from a string containing a json structure"""
        self.raw = json.loads(raw_json)  # Dict[Any, Any]
        self._by_id = {}  # type: Dict[str, Any]
        self._by_metric_name = {}  # type: Dict[str, Any]
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Create some indexes to provide some search shortcuts over data"""
        if not self.is_success():
            return
        for elt in self.raw['data']['result']:
            elt_id = elt['metric']['id']
            to_update_by_id = self._by_id.get(elt_id, [])
            self._by_id[elt_id] = to_update_by_id.append(elt)
            elt_name = elt['metric']['__name__']
            to_update_by_name = self._by_metric_name.get(elt_name, {})
            to_update_by_name[elt_id] = elt
            self._by_metric_name[elt_name] = to_update_by_name

    def is_success (self):
        """Test if the related data is a success or an error
        Returns `True` in case of a success, `False` otherwise
        """
        return self.raw["status"] == 'success'


    def get_metric_values(self, name: str, id: str) -> Any:
        results = self.raw["data"]["result"]
        def somefilter(result):
            tmp = result['metric']
            return tmp['__name__'] == name and tmp['id'] == id
        targets = [tmp for tmp in results if somefilter(tmp)]
        if len(targets) == 1:
            return targets[0]
        else:
            None
