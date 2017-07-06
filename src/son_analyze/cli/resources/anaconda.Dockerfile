FROM jupyter/base-notebook

### Warning: this Dockerfile's context is the root directory of the project

USER root

RUN conda install -y icu

RUN conda install -y openblas

RUN conda install -y numpy=1.13.0 pandas=0.20.2 pyaml=16.12.2 nomkl git pyyaml statsmodels scipy cython matplotlib \
    # Install common packages, Ansible and Git
    && echo 'Done'

WORKDIR /son-analyze

COPY requirements.txt /son-analyze/
COPY son-scikit/requirements.txt /son-analyze/son-scikit/

RUN cd /son-analyze \
    && pip install -r requirements.txt \
    && cd son-scikit \
    && sed -i 's/^son-analyze/# son-analyze/g' requirements.txt \
    && pip install -r requirements.txt \
    && echo 'Done'

COPY . /son-analyze

RUN cd /son-analyze \
    && ./scripts/clean.sh \
    && pip install -r requirements.txt \
    && echo 'Local install' \
    && python3 setup.py develop \
    && cd son-scikit \
    && pip install -r requirements.txt \
    && python3 setup.py develop \
    && echo 'Done'

WORKDIR /home/jovyan/work

USER $NB_USER
