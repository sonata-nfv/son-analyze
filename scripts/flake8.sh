#! /bin/bash -e
# set -x

is_ci() {
    test -n "${JENKINS_URL}"
    return $?
}

run_flake8() {
    >&2 echo -e '*** Running flake8\n'
    if is_ci; then
        flake8 --format='pylint' --output-file="outputs/_output_flake8.out" $@
    else
        flake8 $@
    fi
}

run_flake8 ${@:-setup.py scripts/all.py src/son_analyze tests son-scikit/src/son_scikit son-scikit/tests}
