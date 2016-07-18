#! /bin/bash -e
# set -x

is_ci() {
    test -n "${JENKINS_URL}"
    return $?
}

run_pytest() {
    >&2 echo -e '*** Running py.test\n'
    if is_ci; then
        py.test --junit-xml='outputs/_output_pytest.out' $@
    else
        py.test $@
    fi
}

run_pytest ${@:-tests}
