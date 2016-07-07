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


def build_sonata_df_by_id(prom_data: PrometheusData) -> Dict[str, pandas.DataFrame]:  # pylint: disable=unsubscriptable-object
    """Build a dict of dataframe. Each dataframe contains the values matching
    the corresponding id"""
    # noqa TODO: find the longest metrics and use it as the index. Interpolate the
    # other metric against it before the merge
    result = {}
    for id_index, all_metrics in prom_data._by_id.items():  # pylint: disable=protected-access
        acc_ts = []
        for elt in all_metrics:
            metric_name = elt['metric']['__name__']
            index, data = zip(*elt['values'])
            index = [convert_timestamp_to_posix(z) for z in index]
            this_serie = pandas.Series(data, index)
            this_serie.name = metric_name
            acc_ts.append(this_serie)
        dataframe = pandas.concat(acc_ts, join='outer', axis=1)
        dataframe = dataframe.interpolate(method='time')
        # import pdb; pdb.set_trace()
        result[id_index] = dataframe
    return result
