# pylint: disable=missing-docstring
import typing  # noqa pylint: disable=unused-import
import sys, os
import pytest


def _read_static_fixtures_file(relative_path: str) -> str:
    """Return the content of a fixture file with the relative path
    `relative_path` from the fixtures directory"""
    path = os.path.realpath(os.path.join(sys.modules[__name__].__file__,
                                         '..', 'fixtures',
                                         relative_path))
    with open(path, 'r') as data_file:    
        return data_file.read()


@pytest.fixture
def basic_query_01() -> str:
    return _read_static_fixtures_file('basic_query_01.json')


@pytest.fixture
def empty_result() -> str:
    return _read_static_fixtures_file('empty_result.json')
