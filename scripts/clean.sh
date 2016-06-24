#! /bin/bash -e

if [ -d .tox ]; then
    find .tox -wholename '*/log/*.log' | xargs --no-run-if-empty rm
fi
python3 setup.py clean --all
rm -f dist/* outputs/_output_*
find scripts src tests son-* -type 'd' -iname '*__pycache__' -o -iname '*.egg-info' | xargs --no-run-if-empty rm -r
find scripts src tests son-* -type 'f' -iname '*.pyc' -o -iname '*.pyo' | xargs --no-run-if-empty rm -r
