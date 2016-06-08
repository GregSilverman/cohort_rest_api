from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
from htsql import HTSQL

# Define Flask app
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# import models as a subclass
import models

# misc config objects

URI = 'mysql://test:pw@127.0.0.1/ns_large'
engine = create_engine(URI)
connection = HTSQL(URI)

# CORS request headers
cors = CORS(app, headers="X-Requested-With, Content-Type", resources={r"/*": {"origins": "*"}})

