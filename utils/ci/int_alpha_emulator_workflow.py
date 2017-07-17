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
import socket
import time
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


# pylint: disable=redefined-outer-name
def prune_labeled_containers(docker_client: docker.DockerClient,
                             label: str) -> None:
    entries = docker_client.containers.list(all=True, filters={"label": label})
    for cnt in entries:
        cnt.remove(force=True)


# pylint: disable=redefined-outer-name
def container_is_running(docker_client: docker.DockerClient,
                         name: str) -> bool:
    try:
        docker_client.containers.get(name).status == 'running'
    except docker.errors.NotFound:
        return False
    return True


def _create_son_cli_cnt(docker_client: docker.DockerClient,
                        son_cli_image: str,
                        label: str) -> docker.models.containers.Container:
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
                                           detach=True,
                                           network_mode="host")
    except (docker.errors.ContainerError, docker.errors.APIError) as cntex:
        prune_labeled_containers(docker_client, label)
        pytest.fail("Failure when initiating son-cli: {0!s}".format(cntex))
    return cnt


@pytest.fixture(scope="module")
# pylint: disable=redefined-outer-name
def _son_cli(docker_client: docker.DockerClient,
             son_cli_image: str) -> typing.Iterator[TYPE_SON_CLI]:
    label = "com.sonata.analyze.integration.pytest"
    prune_labeled_containers(docker_client, label)
    cnt = _create_son_cli_cnt(docker_client, son_cli_image, label)
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
        tar.add('msd-sonata_integration.yml')
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
    cnt.kill()
    last_ex = None
    for _ in range(3):
        try:
            docker_client.containers.get(cnt.id)
            cnt.remove(v=True, force=True)
        except docker.errors.NotFound:
            last_ex = None
            break
        except docker.errors.APIError as putex:
            last_ex = putex
        time.sleep(0)
    if last_ex:
        raise last_ex  # pylint: disable-msg=raising-bad-type


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
def msd_service() -> str:
    target = 'msd-sonata_integration.yml'
    path = os.path.realpath(os.path.join(
        sys.modules[__name__].__file__, '..', 'fixtures', target))
    assert os.path.isfile(path)
    return target  # return the path inside the son-cli container


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
# pylint: disable=redefined-outer-name
def test_run(son_cli: TYPE_SON_CLI, service_packages: str,
             docker_client: docker.DockerClient,
             msd_service: str) -> None:
    assert all(elt is not None for elt in [son_cli, service_packages])
    try:
        assert docker_client.containers.get("grafana")
        assert docker_client.containers.get("prometheus")
    except docker.errors.NotFound:
        pytest.fail("The son-monitor's Docker "
                    "containers {0!s} were not found.")
    # server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = "/tmp/.sonata_integration.socket"
    client.connect(path)
    client.send(b'r')
    data = client.recv(len('o'))
    # server.sendto(b'r', path)
    # (data, _) = server.recvfrom(len('o'))
    assert data == b'o'
    client.close()
    # server.shutdown(socket.SHUT_RDWR)
    # time.sleep(14)
    son_cli(30, ["son-access", "config", "--platform_id", "emu", "--new",
                 "--url", "http://127.0.0.1:5000", "--default"])
    for _ in range(20):
        output = son_cli(30, ["son-access", "-p", "emu", "push",
                              "--upload", service_packages]).decode()
        if re.search(r"Upload succeeded \(201\)", output):
            break
        time.sleep(1)
    assert re.search(r"Upload succeeded \(201\)", output)
    to_search = (lambda x: re.search("\"service_instance_uuid\":", x))
    for _ in range(5):
        output = son_cli(30, ["son-access", "-p", "emu", "push",
                              "--deploy", "latest"]).decode()
        if to_search(output):
            break
        time.sleep(1)
    assert to_search(output)
    cnts_running = [False]
    for _ in range(30):
        cnts_running = [container_is_running(docker_client, 'mn.empty_vnf1'),
                        container_is_running(docker_client, 'mn.empty_vnf2'),
                        container_is_running(docker_client, 'mn.empty_vnf3')]
        if all(cnts_running):
            break
        time.sleep(1)
    assert all(cnts_running)
    # output = son_cli(30, ["son-monitor", "msd", "-f", msd_service]).decode()
    # assert re.search(r"msd metrics installed___", output)
    # assert re.search("\"service_instance_uuid\":", output)
    assert True
    # output = son_cli(30, ["son-monitor", "init"])
    # assert re.search(r"Creating grafana", output)
    # time.sleep(5)
    # son_cli(30, ["son-monitor", "interface", "start", "-vnf", "empty_vnf1",
    #              "-me", "tx_packets"])

    # son-monitor interface start -vnf vnf1 -me tx_packets
