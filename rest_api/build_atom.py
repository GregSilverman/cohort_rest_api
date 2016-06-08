#!/usr/bin/env python

from sqlalchemy import between
from sqlalchemy.sql import and_, label

from app import db, models

import htsql_methods as hsql

Clinical = models.ClinicalData
Attribute = models.Attribute

"""
Example SQL atomic query for modified nested model:

 select *
     from
     clinical_data
     (select patient_sid, lft, rgt, a.attribute_id
     from clinical_data
     where attribute_id = 'ID FOR DEMOGRAPHICS') ldl
     on
     cd.patient_sid = ldl.patient_sid
     and
     cd.lft >= ldl.lft
     and
     cd.rgt <= ldl.rgt

     Procedure creates an atomic query, defined by:
     i%2 = 0 -> initial subquery of bucket/attribute

     From above example, the initial subquery that pulls the bucket:

     select patient_sid, lft, rgt, attribute_id
     from clinical_data
     where attribute_id = 'ID FOR DEMOGRAPHICS')

     1%2 != 0 -> drill down to specific bucket attribute

     URL comprised of a single atom will look like:

     atom: demographics:'id for demographics';eq;demographics;demographics:'id for sex';eq;M

     NB: this is attached to incoming requests as a JSON document

     element part 1: bucket
     type:key -> demographics:attribute.id for attribute.value = demographics
     comparator -> eq
     attribute value (bucket) -> demographics
     element part 2: bucket item
     type:key -> demographics:attribute.id for attribute.value = sex
     comparator -> eq
     attribute value -> M

     molecule made up of two atoms: (test_code:'id for test_code';eq;13457-7;test_code:'id for result_value_num';ge;160
     &
     basic_vitals:'id for blood_pressure_systolic';eq;blood_pressure_systolic;basic_vitals:'id for blood_pressure_systolic';ge;160)

    example query:

    select *
     from
     clinical_data cd inner join
     (select  patient_sid, lft as lft_ldl, rgt as rgt_ldl
     from clinical_data
     where string_value = '13457-7' and attribute_id = '12345') ldl
     on
     cd.patient_sid = ldl.patient_sid
     and
     cd.lft >= ldl.lft_ldl
     and
     cd.rgt <= ldl.rgt_ldl
     where double_value >= 160 and attribute_id = '34567'
     order by cd.lft;
"""


# assemble canonical atomic query using parsed components from URL payload
def make_atomic_query(key_type, key, comparator, value, comparator_date, value_date):

    a = []  # atomic array of query elements
    date = []
    whole = [] # entire data set with no constraints

    transform = ['medications', 'demographics']# data need to have special characters removed for querying
    numeric = ['int', 'float', 'double']
    char = ['string']

    # initialize lists
    for i in xrange(0, 2):

        a.append('')
        whole.append('')

        if comparator[i] == 'between':
            arg = value[i].split(',', 2)

        if comparator_date[i]:
            if comparator_date[i] == 'between':
                date = value_date[i].split(',', 2)

    # create queries
    for i in xrange(0, 2):

        # assemble base query
        if i == 0:
            a[i] = db.session.query(Clinical.patient_sid,
                                    Clinical.lft,
                                    Clinical.rgt,
                                    Clinical.attribute_id)
        else:
            a[i] = db.session.query(Clinical.patient_sid,
                                    Clinical.lft,
                                    Clinical.rgt,
                                    label('attribute_value', Clinical.attribute_id),
                                    Clinical.double_value,
                                    Clinical.string_value)

        '''
         equivalent to:

         select  patient_sid, lft, rgt
         from clinical_data
        '''

        # grab the desired bucket
        if i == 0:

            # grab bucket by attribute
            a[i] = a[i].filter(Clinical.attribute_id == int(key[i]))

            '''
             equivalent to:

             select  patient_sid, lft, rgt
             from clinical_data
             where attribute_id = '12345'
            '''

            # NB: these are special characters for building the parse tree -> clean them
            if key_type[i] in transform:
                name = value[i].replace('_', ' ').\
                    replace('{', '('). \
                    replace('}', ')')
            else: name = value[i]

            # grab specific bucket
            a[i] = a[i].filter(Clinical.string_value.op(comparator[i])(name)).subquery()

            '''
             equivalent to:

             select patient_sid, lft, rgt
             from clinical_data
             where string_value = '13457-7' and attribute_id = '12345'
            '''

        # pull item from bucket by attribute name with criterion value
        elif i == 1:

            # grab attribute of interest by name
            '''
            a[i] = a[i].join(a[i-1],
                             and_(Clinical.patient_sid == a[i-1].c.patient_sid,
                                  Clinical.lft >= a[i-1].c.lft,
                                  Clinical.rgt <= a[i-1].c.rgt)).\
                filter(Clinical.attribute_id == key[i])
            '''

            a[i] = a[i].join(a[i-1],
                             and_(Clinical.patient_sid == a[i-1].c.patient_sid,
                                  Clinical.attribute_id == int(key[i]))). \
                filter(Clinical.lft >= a[i-1].c.lft,
                       Clinical.rgt <= a[i-1].c.rgt)

            # unconstrained data set for printing all records
            whole[i] = a[i]

            '''
             equivalent to:

             select patient_sid, lft, rgt
             from
             clinical_data cd inner join
             (select patient_sid, lft, rgt
             from clinical_data
             where string_value = '13457-7' and attribute_id = '12345') ldl
             on
             cd.patient_sid = ldl.patient_sid
             and
             cd.lft >= ldl.lft
             and
             cd.rgt <= ldl.rgt
             where attribute_id = '34567';
            '''

            # flag to control output of all data for desired bucket
            print_all = False

            # for all data for bucket, no filtering is necessary
            if 'OUT' in comparator[i]:
                print_all = True

            if not 'OUT' in comparator[i]:

                qstring = "/attribute{data_type.name}?id='" + key[i] + "'"

                data_type = hsql.get_data(qstring)

                # first: convert to correct data type for utilization of proper covering index
                # NB: default is string

                if data_type in numeric:

                    if comparator[i] != 'between':
                        a[i] = a[i].filter(Clinical.double_value.op(comparator[i])((float(value[i]))))

                    else:
                        a[i] = a[i].filter(between(Clinical.double_value,
                                                   float(arg[0]),
                                                   float(arg[1])))

                elif data_type in char:
                    # clean up incoming string values representative of specific criterion value
                    if key_type[i] in transform:
                        name = value[i].replace('_', ' ').\
                            replace('{', '('). \
                            replace('}', ')')

                    else: name = value[i]

                    a[i] = a[i].filter(Clinical.string_value.op(comparator[i])(name))

                '''
                 equivalent to:
                 select patient_sid, lft, rgt
                 from
                 clinical_data cd inner join
                 (select attribute_id, patient_sid, lft, rgt
                 from clinical_data
                 where string_value = '13457-7' and attribute_id = '12345') ldl
                 on
                 cd.patient_sid = ldl.patient_sid
                 and
                 cd.lft >= ldl.lft
                 and
                 cd.rgt <= ldl.rgt
                 where double_value >= 160 and attribute_id = '34567';
                '''

                # query by date
                if comparator_date[i]:
                    if comparator_date[i] == 'between':
                        a[i] = a[i].filter(between(Clinical.event_date,
                                                   date[0],
                                                   date[1]))

                    else:
                        a[i] = a[i].filter(Clinical.event_date.op(comparator_date[i])([value_date[i]]))


                '''
                 equivalent to:
                 select patient_sid, lft, rgt
                 from
                 clinical_data cd inner join
                 (select attribute_id, patient_sid, lft, rgt
                 from clinical_data
                 where string_value = '13457-7' and attribute_id = '12345') ldl
                 on
                 cd.patient_sid = ldl.patient_sid
                 and
                 cd.lft >= ldl.lft
                 and
                 cd.rgt <= ldl.rgt
                 where double_value >= 160 and attribute_id = '34567'
                 and cd.event_date >= '1/1/1970';
                '''

                # construct final subquery
                a[i] = a[i].subquery()

        else:
            print 'ERROR'

    return a[1], whole[1], print_all


# parse query components: atoms -> particles
# TODO future: implement more general method of mapping using
# http://stackoverflow.com/questions/14845196/dynamically-constructing-filters-in-sqlalchemy
# TODO: implement as parallel loop
def parse_atomic_particles(atom):

    # delimiter between atomic query particles: key, comparator, value
    # used to split atom into particles
    separator = ';'

    # initialize lists
    a = []  # list element for returned atoms
    whole = []

    for i in xrange(0, 1):
        a.append('')
        whole.append('')

    for j in xrange(0, 1):

        # initialize query components
        particles = atom.split(separator, 6)  # atom consists of 6 query components to be parsed, aka particles
        key_type = [] # array of query bucket names
        key = []  # array of key bucket ids
        comparator = []  # array of comparators
        value = []  # array of values
        comparator_date = [] # array of date comparators
        value_date = []  # array of date components

        for i in xrange(len(particles)):
            particle = particles[i]

            # Each atomic unit consists of 6 "particles" delimited by a ';',
            # where each particle consists of a:
            #
            # -> key: representing a bucket name by an attribute
            # -> comparator: representing the logical operation to perform, NB: for bucket this should always be 'eq'
            # -> value: name of bucket
            # -> key: representing an item within the bucket to query by attribute name
            # -> comparator: representing the logical operation to perform on given attribute compared to given value
            # -> value: attribute item's value for comparison

            # map particle components to appropriate lists
            value_comparator_list = ['eq',
                                     'grte',
                                     'lete',
                                     'bt',
                                     'gt',
                                     'lt',
                                     'prn']

            date_comparator_list = ['between',
                                    'grt',
                                    'lss']

            comparator_mapper  = [
                (':', particle.split(':')),
                ('eq', '='),
                ('grte', '>='),
                ('lete', '<='),
                ('bt', 'between'),
                ('between', 'between'),
                ('grt', '>='),
                ('lss', '<='),
                ('lt', '<'),
                ('gt', '>'),
                ('prn', 'OUT')
            ]

            if any(ext in particle for ext in value_comparator_list) or \
                    any(ext in particle for ext in date_comparator_list) or \
                    ':' in particle:

                def apply_mapper(particle):
                    for item, action in comparator_mapper:
                        if item in particle:
                            if ':' in particle:
                                key_type.append(action[0])
                                key.append(action[1])
                                break

                            elif any(ext in particle for ext in value_comparator_list):
                                comparator.append(action)
                                break

                            # date comparison given in value particle
                            elif any(ext in particle for ext in date_comparator_list):
                                # grab operator for date comparison from list
                                date_stuff = particle.split(',DATE,')

                                value.append(date_stuff[0])
                                comparator_date.append(action)

                                # get dates and split in the case of a between comparison
                                date = date_stuff[1].split(',')

                                if len(date) == 2:
                                    temp = date[1]
                                else:
                                    temp = date[1] + ',' + date[2]

                                value_date.append(temp)
                                break
                            else:
                                print'error'

                apply_mapper(particle)
            # if DATE component is not part of value particle use way back in history as default
            else:
                comparator_date.append('>=')
                value_date.append('1776-01-01')
                value.append(particle)

        a[j], whole[j], print_all = make_atomic_query(key_type, key, comparator, value, comparator_date, value_date)

    return a[0], whole[0], print_all

