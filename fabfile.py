from fabric.api import *
from contextlib import contextmanager

#env.directory = '~/development/python/rest_api/rest_api'
env.directory = '/Library/WebServer/wsgi/rest_api/rest_api'
#env.directory = '/var/www/rest_api/rest_api'

env.activate = 'source ' + env.directory + '/venv/bin/activate' # use virtual environment to execute commands

# set context manager to use virtualenv
@contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield


def call( cmd):
    local( cmd, shell="/bin/bash")


# set up environment prior to dev
def prepare():
    with virtualenv():
        #call('git pull')
        call('/bin/bash rest_api/venv/bin/activate')
        call('pip freeze')
        call('pip install -r requirements.txt')
        # ensure correct python from virtual environment is being used
        call('which python')


# create db structure from models
def db_create():
    with virtualenv():
        call('which python')
        call('rest_api/db_create.py')


# make API available
def api():
    with virtualenv():
        call('which python')
        call('rest_api/api.py')


# push change to repo
def scm():
    call('git add --all')
    call('git commit')
    call('git push')

# create db structure from models
def parse():
    with virtualenv():
        call('which python')
        call('rest_api/processTree.py')