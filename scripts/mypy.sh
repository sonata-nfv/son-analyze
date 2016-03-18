#! /bin/bash -e
#set -x

is_ci() {
    test -n "${JENKINS_URL}"
    return $?
}

run_mypy() {
    >&2 echo -e '*** Running mypy\n'
    if is_ci; then
        mypy $@ > outputs/_output_mypy.out
    else
        mypy $@
    fi
}

run_mypy ${@:-setup.py scripts/all.py src/son tests}
