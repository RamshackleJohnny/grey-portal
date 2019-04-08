# TSCT Portal

[![Build Status](https://travis-ci.org/ts-cset/180-project-structure.svg?branch=master)](https://travis-ci.org/ts-cset/180-project-structure)

The unofficial learning management system for Thaddeus Stevens College of Technology built on Python, Flask, and PostgreSQL.


## Installation

Create a virtual environment then install the project:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -e .
```

Developer dependencies can be installed with:

```bash
(venv) $ pip install -e '.[test]'
```

Flask commands require the following environment variables to be set:

```bash
(venv) $ export FLASK_APP=portal
(venv) $ export FLASK_ENV=development
```


## Database Setup

To run the application locally, you need a running instance of PostgreSQL. Create a database and user according to the configuration settings in `portal/__init__.py`. Then you can run the following command to create the necessary tables:

```bash
(venv) $ flask init-db
```

If you want to run tests, you'll have to create a second database according to the configuration in `tests/conftest.py`.


## Running The App

```bash
(venv) $ flask run
```


## Tests and Coverage

```bash
(venv) $ pytest
(venv) $ pytest -v
(venv) $ coverage run -m pytest
```

The first command will run the test functions defined in the `tests/` directory. The second gives a more detailed output. Run the third command to generate a report of the code covered by the tests. You can view this report in the terminal with `coverage report` or with more detail in the browser with `coverage html`.

