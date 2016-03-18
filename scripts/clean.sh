#! /bin/bash -e

find .tox -wholename '*/log/*.log' | xargs --no-run-if-empty rm
python3 setup.py clean --all
py3clean .
rm -f dist/* outputs/_output_*
find scripts src tests -type 'd' -iname '__pycache__' | xargs --no-run-if-empty rm -r
