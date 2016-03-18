#! /bin/bash -e
set -x

docker build -t 'son-analyze-deploy' -f utils/docker/deploy.Dockerfile .

docker build -t 'son-analyze-test' -f utils/docker/test.Dockerfile .

docker run -i --rm=true 'son-analyze-test' scripts/all.py
