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


"""Various utils functions"""


import arrow  # type: ignore
from typing import Any, Tuple  # noqa pylint: disable=unused-import
import pandas  # type: ignore


def reset(arr: Any) -> Any:
    """
    Resets the arrow.Arrow date ``arr`` to 0 second and 0 microsecond
    """
    return arr.replace(second=0, microsecond=0)


def interval_to_now(grace_seconds=-10, **kwargs) -> Tuple[Any, Any]:
    """
    Create a time interval of ``minutes`` minutes.

    Returns a ``(start, end)`` tuple. ``start`` and ``end`` are 2 arrow.Arrow
    objects. The origin time sampled from ``arrow.utcnow()``, shifted
    with a grace period, then reset. ``grace_seconds`` can
    be negative to go back in time. ``kwargs`` are arrow properties. Use plural
    property names to shift time relatively into the past (for example:
    ``minutes=-5``).
    """
    end = reset(arrow.utcnow().shift(seconds=grace_seconds))
    start = end.shift(**kwargs)
    return start, end.shift(seconds=-1)


def smooth_dataframe(dataf: pandas.DataFrame, window=6) -> pandas.DataFrame:
    """Smooth the pandas.DataFrame ``dataf`` corresponding to the ``window``"""
    return dataf.rolling(center=True, window=window) \
                .median() \
                .interpolate(limit_direction='both')
