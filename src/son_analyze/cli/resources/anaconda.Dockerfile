FROM jupyter/base-notebook

### Warning: this Dockerfile's context is the root directory of the project

USER root

RUN conda install -y git pyyaml \
    # Install common packages, Ansible and Git
    && echo 'Done'

WORKDIR /son-analyze

COPY . /son-analyze

RUN cd /son-analyze \
    && ./scripts/clean.sh \
    && pip install -r requirements.txt \
    && echo 'Local install' \
    && python3.5 setup.py develop \
    && cd son-scikit \
    && pip install -r requirements.txt \
    && python3.5 setup.py develop \
    && echo 'Done'

WORKDIR /home/jovyan/work

USER jovyan
