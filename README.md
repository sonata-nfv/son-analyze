# son-analyze

SONATA's Service Platform analysis framework

## Usage

`son-analyze` creates an environment based on the [R language](https://www.r-project.org/) and [RStudio](https://www.rstudio.com/products/rstudio/).

### Commands

* Start by creating the required image on the host with:
    * `son-analyze bootstrap`
        * It will download the official RStudio Docker image and create a new custom Docker image.
        This new image contains a R Sonata library with its required dependencies.
        Please note that the base RStudio image ([rocker/hadleyverse](https://hub.docker.com/r/rocker/hadleyverse/)) size is 2,9 GB.
* Enter the environment with:
    * `son-analyze run`
        * This command will start a Docker container.
    * (Optional) to stop the environment, simply hit `Ctrl-c` in the console.
    * Browse `http://localhost:8787` and enter the default RStudio credentials (`rstudio/rstudio`).
    * Some code examples are provided in the `examples` directory (`File > Open File`).


## Development

### Installation

Ansible & Virtualenv are used to setup the development environment on Ubuntu 14.04:
* Base packages installation
 * `sudo ansible-playbook install.yml`
 * `sudo ansible-playbook dev.install.yml`
* Virtualenv environment creation
 * `virtualenv -p python3 venv`
* Environment activation
 * `source venv/bin/activate`
 * (Optional) Environment deactivation
  * `deactivate`
* Dependencies installation
 * `pip3 install -rrequirements.txt -rdev-requirements.txt`
* Installing `son-analyze`
 * `python setup.py develop`


### Adding/Removing a new dependency

* If the new library is directly used by `son-analyze`:
 * Add the new library to:
  * `setup.py`
  * `requirements.in`
 * Regenerate the dependencies: `pip-compile requirements.in`
* If the new library is only used for testing, developing:
 * Add the new library to:
  * `dev-requirements.in`
  * Regenerate the dependencies: `pip-compile dev-requirements.in`


### Tests and checks

The code is checked and tested by [flake8](https://flake8.readthedocs.org/en/latest/), [pylint](https://www.pylint.org/), [mypy](http://mypy-lang.org/) and [py.test](http://pytest.org/latest/).

Inside a virtualenv environment:
* To Launch all the test: `scripts/all.py`
* Only launch a specific tool globally or on specific files:
 * flake8: `scripts/flake8.sh`
 * pylint: `scripts/pylint.sh setup.py`
 * mypy: `scripts/mypy.sh setup.py src/son/analyze/cli/main.py`
 * py.test: `scripts/py.test.sh`

You can also directly use these tools. 


### Continuous Integration

With Docker, the CI tests can be locally run with:
* `utils/ci/build_01_checks_and_unit_tests.sh`


## Contributing

You may contribute to son-analyze similarly to other SONATA (sub-) projects, i.e. by creating pull requests. The PR code must abide by the `flake8` (pep8) and `pylint` rules.


### Lead Developers

* Geoffroy Chollon (cgeoffroy)
* Steven Van Rossem (stevenvanrossem)
