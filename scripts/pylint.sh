#! /bin/bash -e
# set -x

is_ci() {
    test -n "${JENKINS_URL}"
    return $?
}

run_pylint() {
    >&2 echo -e '*** Running pylint\n'
    if is_ci; then
        pylint --output-format='parseable' $@ > outputs/_output_pylint.out
    else
        pylint --reports=n $@
    fi
}

run_pylint ${@:-setup.py scripts/all.py src/son tests}
