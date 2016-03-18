#! /bin/bash -e
set -x

docker build -t 'son-analyze-deploy' -f utils/docker/deploy.Dockerfile .

docker build -t 'son-analyze-test' -f utils/docker/test.Dockerfile .

if [ -n "${JENKINS_URL}" ]; then
    EXTRA_ENV="JENKINS_URL=${JENKINS_URL}"
fi
docker run -i --rm=true  --env="${EXTRA_ENV}" -v "$(pwd)/outputs:/son-analyze/outputs" 'son-analyze-test' scripts/clean.sh && scripts/all.py
