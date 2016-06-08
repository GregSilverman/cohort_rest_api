#!/usr/bin/env python

from sqlalchemy.sql import label, distinct, literal_column
from sqlalchemy.orm import sessionmaker, joinedload_all
from app import db, models, engine

Clinical = models.ClinicalData
Results = models.Results
Memoize = models.Memoize

import tempfile
import os
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import pandas as pd

# return SQLAlchemy object
def get_query(qtype = 'none', qobject = 'none'):

    if qtype != 'none' and qobject != 'none':

        # built queries for specified subset of patients
        query = db.session.query(label('sid', qobject.c.patient_sid),
                                 label('value_d', qobject.c.double_value),
                                 label('value_s', qobject.c.string_value),
                                 label('attribute', qobject.c.attribute_value))

    elif qtype == 'count' and qobject == 'none':

        # count of patients
        query = db.session.query(distinct(Clinical.patient_sid).label('sid'))


    else:

        # entire population
        query = db.session.query(distinct(Clinical.patient_sid).label('sid'),
                                 literal_column("'complement'").label('attribute'),
                                 literal_column("'0'").label('value_d'),
                                 literal_column("'null'").label('value_s'))


    db.session.commit()
    db.session.close()

    return query

def session():

    session = sessionmaker(bind=engine)
    return session()


def delete_results():

    s = session()

    # delete existing records
    s.query(Results).delete(synchronize_session = False)
    s.commit()
    s.close()


def bulk_insert(arg):

    s = session()

    # insert new records
    s.bulk_insert_mappings(Results, arg)
    s.commit()
    s.close()


def create_record(arg):

    db.session.add(arg)
    db.session.commit()
    db.session.close()


def add_record(arg1, arg2):

    m = Memoize(arg1, arg2)

    db.session.add(m)
    db.session.commit()
    db.session.close()


def get_adjacency(arg):

    # traverse self-referential adjacency list
    # TODO: kludge call specifies "children" 6-levels deep
    # replace with class level eager-loading using join_depth configuration setting
    # could possibly just select entire record
    record = db.session.query(arg). \
        options(joinedload_all("children", "children",
                               "children", "children",
                               "children", "children")).first()

    db.session.close()

    return record


def get_list(query):

    data = pd.read_sql(query.statement, query.session.bind)

    return data.to_dict(orient='records')


def check_exists(arg1):

    test = db.session.query(Memoize.results).filter(Memoize.atom == str(arg1))

    if get_list(test) != []:
        #print 'EXISTS!'
        # get value from dictionary where results is the key
        c =  [str(x['results']) for x in get_list(test)[0:1]]
        #print '!!!!'
        # get as string
        #print c[0]
        # convert string object to list
        #print type(eval(c[0]))
        table = pd.DataFrame(eval(c[0]))
        #print table.sid.nunique()
    else:
        print 'NOT EXISTS!'

