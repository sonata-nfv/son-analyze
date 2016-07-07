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
    hl.build_sonata_df_by_id(x)
