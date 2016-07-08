# pylint: disable=missing-docstring
from time import sleep
from multiprocessing import Process
import typing  # noqa pylint: disable=unused-import
import pytest  # type: ignore
import requests
from docker import Client  # type: ignore
import son_analyze.cli.main
from son_analyze import __version__


@pytest.fixture(scope="session")
def docker_cli():
    return Client(base_url='unix://var/run/docker.sock')


def test_version(capsys) -> None:
    with pytest.raises(SystemExit):
        son_analyze.cli.main.dispatch(['version'])
    out, _ = capsys.readouterr()
    assert out == 'son-analyze version: {}\n'.format(__version__)
    with pytest.raises(SystemExit) as boxed_ex:
        son_analyze.cli.main.dispatch(['version', '--short'])
    out, _ = capsys.readouterr()
    assert out == __version__ + '\n'
    assert boxed_ex.value.code == 0


@pytest.fixture(scope="function")
def run_bg(request):
    run_process = Process(target=son_analyze.cli.main.dispatch,  # type: ignore
                          args=(['run'],))
    run_process.start()  # type: ignore

    def fin():
        run_process.terminate()  # type: ignore
    request.addfinalizer(fin)


@pytest.mark.usefixtures("run_bg")
def test_run(docker_cli) -> None:  # pylint: disable=redefined-outer-name
    req = None
    for _ in range(30):
        try:
            filters = {'label': 'com.sonata.analyze'}
            targets = docker_cli.containers(filters=filters)
            if len(targets) == 1:
                container_id = targets[0].get('Id')
                inspection = docker_cli.inspect_container(container_id)
                container_ip = inspection.get('NetworkSettings') \
                                         .get('IPAddress')
                req = requests.get('http://{}:8888'.format(container_ip))
        except requests.exceptions.ConnectionError:
            pass
        if req and req.status_code == 200:
            break
        sleep(0.2)
    assert req.status_code == 200
    base = '/son-analyze'
    # Verify that the source is here
    cmd = 'find {} -ipath "*son_analyze*" -iname "main.py"'.format(base)
    exec_cmd = docker_cli.exec_create(container=container_id, cmd=cmd)
    exec_out = docker_cli.exec_start(exec_cmd)
    assert exec_out.startswith(str.encode(base))
    # Verify that weird directories were not created
    cmd = 'find {} -ipath "*home*"'.format(base)
    exec_cmd = docker_cli.exec_create(container=container_id, cmd=cmd)
    exec_out = docker_cli.exec_start(exec_cmd)
    assert not exec_out
