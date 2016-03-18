# pylint: disable=missing-docstring
import typing  # noqa pylint: disable=unused-import
import pytest  # type: ignore
import son.analyze.cli.main
from son.analyze import __version__


def test_version(capsys) -> None:
    with pytest.raises(SystemExit):
        son.analyze.cli.main.dispatch(['version'])
    out, _ = capsys.readouterr()
    assert out == 'son-analyze version: {}\n'.format(__version__)
    with pytest.raises(SystemExit) as boxed_ex:
        son.analyze.cli.main.dispatch(['version', '--short'])
    out, _ = capsys.readouterr()
    assert out == __version__ + '\n'
    assert boxed_ex.value.code == 0
