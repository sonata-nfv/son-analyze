"""functions related to prometheus"""

from typing import Any
import json


class PrometheusData:
    """
    The PrometheusData object contains the raw data for a Prometheus
    query
    """

    raw = None  # Dict[Any, Any]

    def __init__(self, raw_json: str) -> None:
        """Constructor from a string containing a json structure"""
        self.raw = json.loads(raw_json)

    def some_method1(self):
        """some_method1"""
        pass

    def some_method2(self):
        """some_method2"""
        pass

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
