REST-API
========

REST API for managing clinical query endpoints

Uses Flask, SQLAlchemy and various libraries

--
Use virtualenv:

- $ virtualenv venv --distribute #install virtualenv
- $ source venv/bin/activate #activate created virtualenv
- $ pip install -r requirements.txt # ensure all requirements are installed in venv

Usage:

* Create database:
$./db_create.py

* Run RESTful web API:
$./api.py

Fab file for builds:

* fab api # run api
* fab db_create #create database
* fab prepare #make sure requirements fulfilled and pull latest codebase
* fab scm # add, commit, push back to repo






