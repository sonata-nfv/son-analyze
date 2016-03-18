FROM son-analyze-deploy:latest

RUN cd /son-analyze/ansible \
    # Start the basic dev Ansible setup
    && ansible-playbook dev.install.yml \
    && cd /son-analyze \
    # Bootstrap the test environment
    && pip3 install -rdev-requirements.txt \
    && echo 'Done'
