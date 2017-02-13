#! /bin/bash -e
set -x


if [ -n "${JENKINS_URL}" ]; then
    echo "Jenkins url detected: ${JENKINS_URL}"
    EXTRA_ENV="JENKINS_URL=${JENKINS_URL}"
fi

docker run -i --rm=true  --env="${EXTRA_ENV}" --env="INTEGRATION_TEST=1" -v "/var/run/docker.sock:/var/run/docker.sock" --workdir '/var/tmp/son.analyze' 'son-analyze:latest' version
