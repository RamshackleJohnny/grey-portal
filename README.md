# TSCT Portal

[![Build Status](https://travis-ci.org/ts-cset/grey-portal.svg?branch=master)](https://travis-ci.org/ts-cset/grey-portal)
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

When you run this command, it will initialize the database. Run the following command to add 2 teachers and 5 students to the database for mock data.

```bash
(venv) $ flask defaults
```

Their credentials are as follows:

**User**: dev@dev.com
**Password**: qwerty

**User**: teacher@teacher.com
**Password**: teacher123

**User**: stu@stu.com
**Password**: student1

**User**: morty@stu.com
**Password**: student2

**User**: jerry@stu.com
**Password**: student3

**User**: michael@stu.com
**Password**: student4

**User**: bichael@stu.com
**Password**: student5

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


## Adding Courses

Navigate to `http://127.0.0.1/courses` and add a course if you're logged in as a teacher. If you created the course, only you can edit and delete the course. Click the trash can that appears to delete the course, or the pencil icon to edit it.

## Adding Users

After exporting `FLASK_APP=portal`, type `flask add-user` in the terminal to add users to the database. There will be a prompt to walk you through adding a new user to the userbase.
