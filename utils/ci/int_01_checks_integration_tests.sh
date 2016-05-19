#! /bin/bash -e
set -x


if [ -n "${JENKINS_URL}" ]; then
    EXTRA_ENV="JENKINS_URL=${JENKINS_URL}"
fi

docker run -i --rm=true  --env="${EXTRA_ENV}" --env="INTEGRATION_TEST=1" -v "/var/run/docker.sock:/var/run/docker.sock" --workdir '/var/tmp/son.analyze' 'son-analyze:latest' /usr/bin/R -e 'devtools::test()'
