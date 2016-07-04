# pylint: disable=missing-docstring
import typing  # noqa pylint: disable=unused-import
#from typing import Dict, Any
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
    x = prometheus.PrometheusData(empty_result)
    assert x.is_success()
    assert x.raw['data']['result'] == []
    assert len(x._by_id) == 0
    assert len(x._by_metric_name) == 0
    x = prometheus.PrometheusData(error_result)
    assert not x.is_success()
    assert len(x._by_id) == 0
    assert len(x._by_metric_name) == 0
