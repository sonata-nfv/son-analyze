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

import typing  # noqa pylint: disable=unused-import
import arrow
import son_scikit.hl_utils as hu


def test_now() -> None:
    tmp = arrow.utcnow()
    assert tmp == tmp.shift(seconds=0)
    n = hu.reset(arrow.utcnow())
    assert n.second == 0
    assert n.microsecond == 0
    (start, end) = hu.interval_to_now(-10, minutes=-1.5, seconds=-30)
    assert end.second == 59
    assert len(arrow.Arrow.range('second', start, end)) == 120
