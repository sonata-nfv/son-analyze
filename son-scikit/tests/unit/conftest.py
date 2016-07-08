# pylint: disable=missing-docstring
import sys
import os
import typing  # noqa pylint: disable=unused-import
from pkg_resources import resource_filename  # type: ignore
import pytest  # type: ignore


def _find_sonanalyze_fixtures() -> str:
    path = os.path.realpath(resource_filename('son_analyze', '../..'))
    return os.path.join(path, 'tests/unit/fixtures')


def _read_static_fixtures_file(relative_path: str,
                               from_sonanalyze=False) -> str:
    """Return the content of a fixture file with the relative path
    `relative_path` from the fixtures directory"""
    base = os.path.join(sys.modules[__name__].__file__, '..', 'fixtures')
    if from_sonanalyze:
        base = _find_sonanalyze_fixtures()
    path = os.path.realpath(os.path.join(base, relative_path))
    with open(path, 'r') as data_file:
        return data_file.read()


@pytest.fixture
def basic_query_01() -> str:
    return _read_static_fixtures_file('basic_query_01.json', True)
