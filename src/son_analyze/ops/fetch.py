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


"""son-analyze fetch operation"""

import os
from enum import Enum
import logging
import collections
from urllib.parse import ParseResult, urljoin
from typing import Dict, Any, Tuple, List
import requests


_LOGGER = logging.getLogger(__name__)


class FetchError(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidResourceReferenceError(FetchError):
    """Raised when a resource (nfd) points to a missing vnfd."""

    # pylint: disable=unsubscriptable-object
    def __init__(self, nsd: Dict[str, Any], missing_vnf_id: str) -> None:
        super().__init__()
        self.nsd = nsd
        self.missing_vnf_id = missing_vnf_id
        self.message = ('The nsd ("{}","{}","{}") has a vnf_id field "{}" '
                        'pointing to a non-existing vnfd').format(
                            nsd['vendor'], nsd['name'], nsd['version'],
                            missing_vnf_id)


def _get_workspace_token(workspace_dir: str) -> str:
    """Retrieve the authentification token from the workspace"""
    _LOGGER.debug('Computing the Sonata workspace from: %s', workspace_dir)
    path = os.path.join(workspace_dir, 'platforms',
                        'token.txt')
    if os.path.isfile(path) and os.access(path, os.R_OK):
        with open(path) as tkn:
            return tkn.read()
    else:
        _ = 'The Sonata token file {} is not a readable file'.format(path)
        exc = RuntimeError(_)
        _LOGGER.error('Error when reading the Sonata auth token: %s', exc)
        raise exc


class Kind(Enum):
    """The different available resources"""
    nsd = 1
    vnfd = 2
    vnfr = 3
    nsr = 4


def _get_path_from_kind(kind: Kind) -> str:
    """Return the api path for a given resource kind"""
    table = {
        Kind.nsd: 'services',
        Kind.vnfd: 'functions',
        Kind.vnfr: 'records/functions',
        Kind.nsr: 'records/services'
    }
    try:
        return table[kind]
    except KeyError:
        _ = "Cannot compute the fetch api path for {}".format(kind)
        raise RuntimeError(_)


def _get_childrend_kind(kind: Kind) -> Kind:
    """Return the kind of resources that can be embedded in the `kind` Kind."""
    table = {
        Kind.nsd: Kind.vnfd,
        Kind.vnfd: None,
        Kind.vnfr: None,
        Kind.nsr: Kind.vnfr
    }
    try:
        return table[kind]
    except KeyError:
        _ = "Cannot compute the children kind for {}".format(kind)
        raise RuntimeError(_)


FETCHTYPE = Tuple[Dict[str, Any], List[Dict[str, Any]]]


# pylint: disable=unsubscriptable-object,too-many-arguments
def fetch_resource_by_uuid(gatekeeper_endpoint: ParseResult,
                           workspace_dir: str, kind: Kind,
                           uuid: str) -> Dict[str, Any]:
    """Fetch a resource by its uuid. Return `None` if nothing is found.
    Raise a RuntimeError exception when a error is detected within the
    gatekeeper's API."""
    url = urljoin(gatekeeper_endpoint.geturl(),
                  os.path.join(_get_path_from_kind(kind), uuid))
    _LOGGER.info('Fetching a resource by uuid at %s', url)
    auth = 'Bearer ' + _get_workspace_token(workspace_dir)
    res_resp = requests.get(url, headers={'content-type': 'application/json',
                                          'Authorization': auth})
    try:
        res_resp.raise_for_status()
    except requests.exceptions.HTTPError as exc_notfound:
        _LOGGER.exception('Failed to retrieve a resource at %s '
                          '(status code = %d)', res_resp.url,
                          res_resp.status_code)
        if exc_notfound.response.status_code == 404:
            return None
        else:
            raise
    tmp = res_resp.json()
    if not isinstance(tmp, dict) or len(tmp) <= 0:
        exc = RuntimeError('The returned json is malformed:  {}'.format(tmp))
        _LOGGER.error('Error while fetching a resource using an uuid: %s', exc)
        raise exc
    _LOGGER.info('Succeed to retrieve the resource %s (status code = %d)',
                 res_resp.url, res_resp.status_code)
    if kind.name in tmp:  # the resource is boxed
        tmp = tmp[kind.name]
    return tmp


# pylint: disable=unsubscriptable-object
def fetch_resource(gatekeeper_endpoint: ParseResult, workspace_dir: str,
                   kind: Kind, vendor: str, name: str,
                   version: str) -> Tuple[str, Dict[str, Any]]:
    """Fetch a resource and return the Json as a dictionary. Return `None` if
     nothing is found. It raise a RuntimeError exception when a gatekeeper API
     is dectected"""
    url = urljoin(gatekeeper_endpoint.geturl(), _get_path_from_kind(kind))
    _LOGGER.info('Fetching a %s resource by name at %s', kind, url)
    query_params_raw = {'vendor': vendor,  # Dict[Str, Str]
                        'name': name,
                        'version': version}
    # We force the order of the query's parameters to lower the impact on tests
    # when a key is added or removed
    query_params = collections.OrderedDict(sorted(query_params_raw.items()))
    auth = 'Bearer ' + _get_workspace_token(workspace_dir)
    res_resp = requests.get(url, params=query_params,
                            headers={'content-type': 'application/json',
                                     'Authorization': auth})
    try:
        res_resp.raise_for_status()
    except requests.exceptions.HTTPError:
        _LOGGER.exception('Failed to retrieve a resource at %s '
                          '(status code = %d)', res_resp.url,
                          res_resp.status_code)
        # REMARK: if nothing is found, then the API return an empty [] and
        # not 404
        raise
    tmp = res_resp.json()
    if not isinstance(tmp, list):
        exc = RuntimeError('The returned json is not boxed by a list')
        _LOGGER.error('The GK API must return a list of resources: %s', exc)
        raise exc
    _LOGGER.info('Succeed to retrieve the resource %s (status code = %d): %s',
                 res_resp.url, res_resp.status_code, tmp[:20])
    for elt in tmp:
        this_uuid = elt['uuid']
        if not this_uuid:
            _LOGGER.warning('Ignoring an element without id or uuid: %s', elt)
            continue
        if kind.name in elt:  # the resource is boxed
            elt = elt[kind.name]
        if all([elt['vendor'] == vendor, elt['name'] == name,
                elt['version'] == version]):
            return (this_uuid, elt)
    return None


# pylint: disable=unsubscriptable-object
def _complete_nsd_with_vnfds(gatekeeper_endpoint: ParseResult,
                             workspace_dir: str, uuid: str,
                             nsd: Dict[str, Any],
                             kchildren: Kind) -> FETCHTYPE:
    """Retrieve the vnfds mentioned in a nsd. Raise a
    InvalidResourceReferenceError exception if a vnfd is missing."""
    _LOGGER.info('Fetching the inner vnfds of the %s nsd', uuid)
    acc = []  # List[Dict[str, Any]]
    for fun_desc in nsd['network_functions']:
        if 'vnfr_id' in fun_desc:
            vnfd = fetch_resource_by_uuid(gatekeeper_endpoint, workspace_dir,
                                          kchildren, fun_desc['vnfr_id'])
        else:
            (_, vnfd) = fetch_resource(gatekeeper_endpoint, workspace_dir,
                                       kchildren, fun_desc['vnf_vendor'],
                                       fun_desc['vnf_name'],
                                       fun_desc['vnf_version'])
        if not vnfd:
            exc = InvalidResourceReferenceError(nsd, fun_desc['vnf_id'])
            _LOGGER.error('Error when retrieving a vnfd: %s', exc)
            raise exc
        acc.append(vnfd)  # FIX: check for uniqueness ?
    return (nsd, acc)


# pylint: disable=unsubscriptable-object
def fetch_resources(gatekeeper_endpoint: ParseResult, workspace_dir: str,
                    kind: Kind, vendor: str, name: str,
                    version: str) -> FETCHTYPE:
    """Fetch a main resource and its sub-elements"""
    (uuid, base) = fetch_resource(gatekeeper_endpoint, workspace_dir, kind,
                                  vendor, name, version)
    kchildren = _get_childrend_kind(kind)
    if base and kchildren:
        return _complete_nsd_with_vnfds(gatekeeper_endpoint, workspace_dir,
                                        uuid, base, kchildren)
    return base, []


# pylint: disable=unsubscriptable-object,too-many-arguments
def fetch_resources_by_uuid(gatekeeper_endpoint: ParseResult,
                            workspace_dir: str, kind: Kind,
                            uuid: str) -> FETCHTYPE:
    """Fetch a main resource and its sub-element"""
    base = fetch_resource_by_uuid(gatekeeper_endpoint, workspace_dir, kind,
                                  uuid)
    kchildren = _get_childrend_kind(kind)
    if base and kchildren:
        return _complete_nsd_with_vnfds(gatekeeper_endpoint, workspace_dir,
                                        uuid, base, kchildren)
    return base, []
