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


"""son-analyze fetch command"""

# pylint: disable=unsubscriptable-object
from enum import Enum
import logging
from urllib.parse import ParseResult
from typing import Dict, Iterable, Any
import yaml  # type: ignore
from son_analyze.ops import fetch
from son_analyze.core import types


_LOGGER = logging.getLogger(__name__)


def _print_yml_to_stdout(values: Iterable[Dict[str, Any]]) -> None:
    """Print the fetch result to the console."""
    print(yaml.dump_all(values))


def _not_available(*_):
    """Dummy function to fill the fetch operation on some kind"""
    _ = ("Fetching this kind of resource is not possible when using the"
         "name,vendor,version format")
    raise RuntimeError(_)


class _Dispatcher(Enum):
    vnfd = (fetch.fetch_vnfd_by_uuid, fetch.fetch_vnfd)
    nsd = (fetch.fetch_nsd_by_uuid, fetch.fetch_nsd)
    vnfr = (fetch.fetch_vnfr_by_uuid, _not_available)
    nsr = (fetch.fetch_nsr_by_uuid, _not_available)

    def __init__(self, ffetch_by_uuid, ffetch):
        self.fetch_by_uuid = ffetch_by_uuid
        self.fetch = ffetch


def fetch_cmd(gatekeeper: ParseResult, workspace_path: str, skind: str,
              target: types.ResourceTargetTuple) -> None:
    """Fetch a vnfd or a nsd (with its dependencies) and display the result
     as Yaml documents on STDOUT."""
    try:
        kind = _Dispatcher[skind]  # type: ignore
    except KeyError:
        raise RuntimeError('Invalid resource type {}'.format(skind))
    if target.uuid:
        res = kind.fetch_by_uuid(gatekeeper, workspace_path, target.uuid)
    else:
        res = kind.fetch(gatekeeper, workspace_path, target.vendor,
                         target.name, target.version)
    if isinstance(res, tuple):
        base, docs = res
        _print_yml_to_stdout([base] + docs)
    else:
        _print_yml_to_stdout([res])
    return
