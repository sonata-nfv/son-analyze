# FROM alpine:3.6

# RUN apk update && \
#     apk add --no-cache ca-certificates wget bash iperf3 gcc python3 python3-dev libffi-dev musl-dev openssl-dev && \
#     wget https://bootstrap.pypa.io/get-pip.py && \
#     python3 get-pip.py && \
#     rm get-pip.py && \
#     pip3 install treq

FROM ubuntu:xenial

RUN apt-get update && \
    apt-get install -y wget python3 python3-dev iperf3 gcc libssl-dev siege libffi-dev net-tools iproute inetutils-ping && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    pip3 install treq

ENV SON_EMU_CMD echo "son-analyze integration cnt ready"

COPY p.py /

# ENTRYPOINT ["/usr/bin/tail", "-F", "-s", "600", "/dev/null"]
