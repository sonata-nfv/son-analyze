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


"""son-analyze batch operations"""

import logging
from urllib.parse import ParseResult, urljoin
import datetime
from typing import Iterable, List, Tuple
import requests


_LOGGER = logging.getLogger(__name__)


def _create_batches(start: int, end: int,
                    batch_size: int) -> List[Tuple[int, int]]:
    """Returns a list of interval between ``start`` and ``end``."""
    basel = range(start, end, batch_size)  # type: Iterable[int]
    res = list(map(lambda elt: (elt, elt + batch_size - 1), basel))
    if end % batch_size != 0 and res:
        subs, _ = res[-1]  # type: Tuple[int, int]
        res[-1] = subs, subs + (end - start) % batch_size
    return res


# pylint: disable=unused-argument
def batch_raw_query(prometheus_endpoint: ParseResult,
                    start_timestamp: int,
                    end_timestamp: int,
                    step: datetime.timedelta,
                    query: str) -> bytes:
    """Retrieve metrics from a Prometheus database"""
    payload = {'query': query,
               'start': start_timestamp,
               'end': end_timestamp,
               'step': '{}s'.format(int(step.total_seconds()))}
    url = urljoin(prometheus_endpoint.geturl(), 'api/v1/query_range')
    req = requests.get(url, params=payload)
    return req.content
