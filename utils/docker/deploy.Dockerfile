FROM ubuntu:14.04

RUN apt-get update \
    # Install common packages
    && apt-get install -y software-properties-common apt-transport-https ca-certificates wget \
    # Install Ansible and Git
    && apt-add-repository ppa:ansible/ansible \
    && apt-get update \
    && apt-get install -y ansible git \
    # Add the localhost to the Ansible's hosts
    && echo 'localhost ansible_connection=local' >> /etc/ansible/hosts \
    # Pre-install python 3.4 and pip3 to speed-up the next steps
    && apt-get install -y python3.4 python3-pip libyaml-dev \
    && echo 'Done'

WORKDIR /son-analyze

COPY . /son-analyze

RUN cd /son-analyze/ansible \
    # Start the basic Ansible setup
    && ansible-playbook install.yml \
    && cd /son-analyze \
    && ./scripts/clean.sh \
    # Creating the son-analyze wheel
    && python3.4 setup.py bdist_wheel \
    # Install the son-analyze package from a local wheel
    && pip3 install dist/son_analyze-*-py3-*.whl \
    && echo 'Done'
