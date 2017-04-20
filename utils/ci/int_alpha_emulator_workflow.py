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


# pylint: disable=missing-docstring
import os
import sys
import logging
import tarfile  # type: ignore
import re
import io
import typing  # noqa pylint: disable=unused-import
import pytest  # type: ignore
import docker  # type: ignore


_LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def docker_client() -> docker.DockerClient:
    yield docker.from_env()


@pytest.fixture(scope="module")
# pylint: disable=redefined-outer-name
def son_cli_image(docker_client: docker.DockerClient) -> str:
    target = "registry.sonata-nfv.eu:5000/son-cli:latest"
    try:
        docker_client.images.get(target)
    except docker.errors.ImageNotFound:
        pytest.fail("The Docker image {0!s} was not found.".format(target))
    return target


TYPE_SON_CLI = typing.Callable[[int, typing.List[str]], bytes]


def prune_labeled_containers(docker_client: docker.DockerClient,
                             label: str) -> None:
    entries = docker_client.containers.list(all=True, filters={"label": label})
    for cnt in entries:
        cnt.remove(force=True)


@pytest.fixture(scope="module")
# pylint: disable=redefined-outer-name
def _son_cli(docker_client: docker.DockerClient,
             son_cli_image: str) -> typing.Iterator[TYPE_SON_CLI]:
    label = "com.sonata.analyze.integration.pytest"
    prune_labeled_containers(docker_client, label)
    cnt = None
    entrypoint = ["/usr/bin/tail", "-s", "600", "-F", "/dev/null"]
    try:
        cnt = docker_client.containers.run(image=son_cli_image,
                                           command=[],
                                           entrypoint=entrypoint,
                                           labels=[label],
                                           # remove=True,
                                           # volumes=volumes,
                                           working_dir="/root",
                                           stderr=True,
                                           detach=True)
    except (docker.errors.ContainerError, docker.errors.APIError) as cntex:
        prune_labeled_containers(docker_client, label)
        pytest.fail("Failure when initiating son-cli: {0!s}".format(cntex))
    with io.BytesIO() as tarstream:
        base = os.path.realpath(os.path.join(
            sys.modules[__name__].__file__,
            '..',
            'fixtures/sonata-integration'))
        (root, target) = os.path.split(base)
        tar = tarfile.TarFile(fileobj=tarstream, mode='w')
        org = os.getcwd()
        os.chdir(root)
        tar.add(target)
        tar.close()
        os.chdir(org)
        tarstream.seek(0)
        try:
            put_res = cnt.put_archive("/root", tarstream)
            if not put_res:
                cnt.remove(force=True)
                pytest.fail("Invalid result when copying"
                            " the service package sources")
        except docker.errors.APIError as putex:
            cnt.remove(force=True)
            pytest.fail("Low level failure when copying the "
                        "service package sources: {0!s}".format(putex))

    def run_in_son_cli(timeout_sec: int, command: typing.List[str]) -> bytes:
        entrypoint = (["/usr/bin/timeout", "-s", "KILL", str(timeout_sec)] +
                      command)
        tmp = b""  # type: bytes
        try:
            tmp = cnt.exec_run(cmd=entrypoint)
        except docker.errors.APIError as runex:
            pytest.fail("A son-cli command failed: {0!s}".format(runex))
        return tmp

    yield run_in_son_cli
    cnt.remove(force=True)


@pytest.fixture(scope="module")
# pylint: disable=redefined-outer-name
def son_cli(_son_cli: TYPE_SON_CLI) -> TYPE_SON_CLI:
    tmp = _son_cli(30, ["son-workspace", "--init"])
    if not re.search("Creating workspace at /root/.son-workspace",
                     tmp.decode()):
        pytest.fail("Failed to create the workspace: {0!s}"
                    .format(tmp.decode()))
    return _son_cli


@pytest.fixture(scope="module")
# pylint: disable=redefined-outer-name
def vnf_image(docker_client: docker.DockerClient):
    path = os.path.realpath(os.path.join(
        sys.modules[__name__].__file__, '..', 'fixtures'))
    docker_client.images.build(path=path,
                               tag="integration-sonata",
                               dockerfile="Dockerfile",
                               rm=True)
    _LOGGER.debug("Docker image built")
    return "integration-sonata"


@pytest.fixture(scope="module")
# pylint: disable=redefined-outer-name
def service_packages(son_cli: TYPE_SON_CLI, vnf_image) -> str:
    assert vnf_image is not None
    tmp = son_cli(60,
                  ["son-package", "--project", "sonata-integration"]).decode()
    check = [re.search("Package generated successfully", tmp),
             re.search("File: /root/eu.sonata-nfv.pack"
                       "age.sonata-empty-service.0.4.son", tmp)]
    if not all(check):
        pytest.fail("Failed to create the service package: {0!s}".format(tmp))
    return "/root/eu.sonata-nfv.package.sonata-empty-service.0.4.son"


@pytest.mark.integration
def test_run() -> None:
    assert True
