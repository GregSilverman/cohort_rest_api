#!/usr/bin/env python
from gevent import monkey
monkey.patch_all()
from flask import request, jsonify
from marshmallow import Schema, fields
import time

# kludge for running pandas locally in testing mode
import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import pandas as pd

from flask_cors import cross_origin

# load extensions
from app import app, models, connection

import htsql_methods

#import sqla_methods

# compile Cython objects

build_dir = '/Library/WebServer/wsgi/rest_api'

import pyximport; pyximport.install(build_dir)
import build_atom

#import pyximport; pyximport.install(build_dir)
build_dir = 'Library/WebServer/wsgi/rest_api'
import sqla_methods

#import pyximport; pyximport.install(build_dir)
#import set_operations

import evaluate as eval

# Classes used in API calls
Query = models.Query
Medications = models.Meds_Menu

#http://mortoray.com/2014/04/09/allowing-unlimited-access-with-cors/
@app.after_request
def add_cors(resp):
    """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    resp.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', 'Authorization')
    # set low for debugging
    if app.debug:
        resp.headers['Access-Control-Max-Age'] = '1'

    return resp


@app.route("/")
def index():
    return 'Hello!'


# endpoint for QT data store with Ajax proxy for populating dynamic control
@app.route('/menu/<criterion>', methods=['GET', 'POST', 'OPTIONS'])
def get_menu(criterion):

    query = "/menu_test{code,description+,code_description}?menu_type='" + criterion + "'"

    json = htsql_methods.get_data_json(query)

    return json


# endpoint for QT data store with Ajax proxy for populating dynamic control
@app.route('/attribute', methods=['GET', 'POST', 'OPTIONS'])
def get_attribute():

    query = "/attribute{id,attribute_value}"

    json = htsql_methods.get_data_json(query)

    return json


# endpoint for QT data store with Ajax proxy for populating dynamic control
@app.route('/basic_vitals/', methods=['GET', 'POST', 'OPTIONS'])
def get_basic_vitals():

    query = "/basic_vitals_units{measure+,units,field_name}"

    json = htsql_methods.get_data_json(query)

    return json

# parse and run molecule payload as query


# endpoint for QT data store with Ajax proxy for populating dynamic control
@app.route('/labs/', methods=['GET', 'POST', 'OPTIONS'])
def get_labs():

    query = "/lab_units{code,description+,units}"

    json = htsql_methods.get_data_json(query)

    return json


@app.route('/submit_query/', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def submit_query():

    start = time.time()

    # get POSTed JSON
    json = request.get_json()
    payload = json['query']['payload']

    # payload is unicode encoded
    payload = payload.encode('ascii')

    results = eval.process_sentence(payload)

    # write output to table
    #sqla_methods.delete_results()
    # insert new records
    #sqla_methods.bulk_insert(results)

    # check that results set is not the empty set
    empty_set = [{'attribute': 'null', 'value_d': 0, 'value_s': 'null', 'sid': 0}]
    diff = [x for x in results if x not in empty_set]

    if len(diff) != 0:
        #print 'results'
        #print results
        #print type(results)
        table = pd.DataFrame(results)
        count = table.sid.nunique()
    else:
        count = 0
        #sqla_methods.delete_results()

    #patients = pd.DataFrame(sqla_methods.get_list(sqla_methods.get_query('count')))
    total = 28253 # patients.sid.nunique()

    elapsed = (time.time() - start)

    print '!!!!!'
    print elapsed

    return jsonify({'items': count, 'total': total})


# write test query to database
@app.route('/remote_query_put', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin() # allow all origins all methods
def write_query():
    # Get the parsed contents of Ajax request
    json = request.get_json()

    # define dictionary item for entire object
    query = json['query']

    # insert into tables
    q = Query(molecule=query['molecule'],
              query_name=query['query_name'],
              remote_user='gms', #request.remote_user,
              criteria=query['criteria'])

    sqla_methods.create_record(q)

    return jsonify(json)


# get returned results
@app.route('/remote_results_get', methods=['GET', 'POST', 'OPTIONS'])
def read_results():

    query = "/results{sid,attribute+,value_s,value_d}" # ?user='gms'")

    json = htsql_methods.get_data_json(query)

    return json


# get saved queries
@app.route('/remote_query_get', methods=['GET', 'POST', 'OPTIONS'])
def read_query():

    query = "/cc_query{query_name,criteria,remote_user,molecule+}" #+ request.remote_user + "'")

    json = htsql_methods.get_data_json(query)

    return json


# get saved queries
@app.route('/total', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin() # allow all origins all methods
def count_patients():

    table = pd.DataFrame(sqla_methods.get_list(sqla_methods.get_query('count')))
    count = table.sid.nunique()

    return jsonify(n=count)


# get meds adjacency list as nested JSON
@app.route('/meds', methods=['GET', 'POST', 'OPTIONS'])
def test():

    record = sqla_methods.get_adjacency(Medications)

    class TestSchema(Schema):
        name = fields.Str()
        type = fields.Str()
        iconCls = fields.Str()
        id = fields.Int(dump_only=True)
        parent_id = fields.Int(dump_only=True)
        children = fields.Nested('self', many=True)
        drug_code = fields.Str()
        leaf = fields. Boolean()

    schema = TestSchema()

    result = schema.dump(record)

    #pprint(result.data)

    return jsonify(children=result.data)


if __name__ == '__main__':

    # Start app
    app.run(debug=True, use_reloader=True)

