import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Prevent cross-site request forgery
WTF_CSRF_ENABLED = True

# Dummy secret key so we can use sessions - use with CSRF
SECRET_KEY = '123456790'

# db connection string
SQLALCHEMY_DATABASE_URI = 'mysql://test:pw@127.0.0.1/ns_large'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_SIZE = 200
SQLALCHEMY_stream_results = False
#SQLALCEMY_rollback_returned = False
#SQLALCHEMY_autoflush = False
SQLALCHEMY_ECHO = False

CORS_HEADERS = 'Authorization, Content-Type, X-Auth-Token, X-Requested-With'

