__author__ = 'bhavtosh'

'''The method uses the diff. lists generated from parse_atomic_particles to form sql queries.'''

from tests.TEST_parse_atomic_particles import comparator, value, comparator_date, value_date, key
from sqlalchemy.sql import and_
from sqlalchemy import between


#def make_atomic_query(key, comparator, value, comparator_date, value_date, neg):

Clinical = models.ClinicalData
Attribute = models.Attribute
debug = False

# Example atomic query:

# select *
# from
# clinical_data cd inner join attribute a on
# a.id = cd.attribute_id inner join
# (select patient_sid, lft, rgt, a.attribute_value
# from clinical_data cd inner join attribute a on
# a.id = cd.attribute_id
# where a.attribute_value = 'DEMOGRAPHICS') ldl
# on
# cd.patient_sid = ldl.patient_sid
# and
# cd.lft >= ldl.lft
# and
# cd.rgt <= ldl.rgt

# Creates an atomic query, defined by:
# i%2 = 0 -> initial subquery of bucket/attribute
#
# From above, the initial subquery that pulls the bucket:
#
# select patient_sid, lft, rgt, a.attribute_value
# from clinical_data cd inner join attribute a on
# a.id = cd.attribute_id
# where a.attribute_value = 'DEMOGRAPHICS')
#
# 1%2 != 0 -> drill down to specific bucket attribute

# TEST URL will look like:

# comprised of a single atom: sex:demographics;eq;demographics;demographics;sex:sex;eq;M
# http://127.0.0.1:5000/get_query/(sex:demographics;eq;demographics;sex:sex;eq;M)
#
# element part 1: bucket
# key -> sex:demographics
# comparator -> eq
# attribute value (bucket) -> demographics
# element part 2: bucket item
# key -> sex:sex
# comparator -> eq
# attribute value -> M
#
# comprised of a molecule made up of two atoms: lab:test_code;eq;13457-7;lab:result_value_num;ge;160
# &
# vital:blood_pressure;eq;blood_pressure;vital:blood_pressure_systolic;ge;160
#
# 127.0.0.1:5000/api/get_query/(lab:test_code;eq;13457-7;lab:result_value_num;ge;160)&
# (vital:blood_pressure;eq;blood_pressure;vital:blood_pressure_systolic;ge;160)

# example query:
#select *
# from
# clinical_data cd inner join
# (select  patient_sid, lft as lft_ldl, rgt as rgt_ldl
# from clinical_data cd join attribute a on a.id = cd.attribute_id
# where string_value = '13457-7' and a.attribute_value = 'test_code') ldl
# on
# cd.patient_sid = ldl.patient_sid
# and
# cd.lft >= ldl.lft_ldl
# and
# cd.rgt <= ldl.rgt_ldl inner join
# attribute a on
# cd.attribute_id = a.id
# where double_value >= 160 and a.attribute_value = 'result_value_num'
# order by cd.lft;

a = []  # atomic array of query elements
date = []

# initialize lists
for i in range(0, 2):
    a.append('')
    print '## a is: ', a
# create queries
for i in range(0, 2):

    # assemble base query
    a[i] = db.session.query(Clinical.patient_sid,
                            Clinical.lft,
                            Clinical.rgt)
    print '## a[] is: ', a[i]

    # equivalent to:
    # select  patient_sid, lft, rgt
    # from clinical_data

    if debug:
            print 'i is:'
            print str(i)

    print '## comparator[i] izzz: ', comparator[i]

    if comparator[i] == 'between':
        arg = value[i].split(',', 2)
        print '## value[i] izzz: ', value[i]
        if debug:
            print 'arg!'
            print str(arg[1]) + ' ' + str(arg[0])

    if comparator_date[i]:
        if comparator_date[i] == 'between':
            date = value_date[i].split(',', 2)

            if debug:
                print 'split date val!'
                print str(date[1]) + ' ' + str(date[0])

    elif comparator_date[i] != 'between':
        if debug:
            print 'date val!'
            print str(value_date[i])

    # grab the desired bucket
    if i == 0:

        # grab bucket by attribute
        a[i] = a[i].join(Attribute,
                         Attribute.id == Clinical.attribute_id). \
            filter(Attribute.attribute_value.op('=')([key[i]]))

        # equivalent to
        # select  patient_sid, lft, rgt
        # from clincial_data cd join attribute a on a.id = cd.attribute_id
        # where a.attribute_value = 'test_code'

        # grab specific bucket
        a[i] = a[i].filter(Clinical.string_value.op('=')([value[i]])).subquery()
        print '## a[i] for i=0 (with JOIN and filter) is: ', a[i]
        print '## value[i] for i=0 is: ', value[i]
        # equivalent to:
        # select patient_sid, lft, rgt
        # from clinical_data cd join attribute a on a.id = cd.attribute_id
        # where string_value = '13457-7' and a.attribute_value = 'test_code'

        if debug:
            print 'bucket name:'
            print key[i]
            print a[0]

    # pull item from bucket by attribute name with criterion value
    elif i == 1:

        # grab attribute of interest by name
        a[i] = a[i].join(Attribute,
                         Attribute.id == Clinical.attribute_id). \
            join(a[i-1],
                 and_(Clinical.lft >= a[i-1].c.lft,
                      Clinical.rgt <= a[i-1].c.rgt,
                      Clinical.patient_sid == a[i-1].c.patient_sid)). \
            filter(Attribute.attribute_value.op('=')([key[i]]))

        print '## a[i] for i=1 (with JOIN and filter) is: ', a[i]
        print '## key[i] for i=1 is: ', key[i]
        # equivalent to
        # select patient_sid, lft, rgt
        # from
        # clinical_data cd inner join
        # (select patient_sid, lft, rgt
        # from clinical_data cd join attribute a on a.id = cd.attribute_id
        # where string_value = '13457-7' and a.attribute_value = 'test_code') ldl
        # on
        # cd.patient_sid = ldl.patient_sid
        # and
        # cd.lft >= ldl.lft
        # and
        # cd.rgt <= ldl.rgt inner join
        # attribute a on
        # cd.attribute_id = a.id
        # where a.attribute_value = 'result_value_num';

        # handle case where list of numbers passed for between operator by stripping off ',' then query by value
        print '## value[i] is: ', value[i]

        if value[i].replace(',', '').isdigit():

            if debug:
                print 'Is a digit'
            print '## comparator[i] is: ', comparator[i]
            if comparator[i] != 'between':

                a[i] = a[i].filter(Clinical.double_value.op(comparator[i])((value[i])))

            else:

                a[i] = a[i].filter(between(Clinical.double_value,
                                               arg[0],
                                               arg[1]))

                print '## arg[0] is: ', arg[0]
                print '## arg[1] is: ', arg[1]

        else:
            a[i] = a[i].filter(Clinical.string_value.op(comparator[i])((value[i])))

        # select patient_sid, lft, rgt
        # from
        # clinical_data cd inner join
        # (select attribute_value, patient_sid, lft, rgt
        # from clinical_data cd join attribute a on a.id = cd.attribute_id
        # where string_value = '13457-7' and a.attribute_value = 'test_code') ldl
        # on
        # cd.patient_sid = ldl.patient_sid
        # and
        # cd.lft >= ldl.lft
        # and
        # cd.rgt <= ldl.rgt inner join
        # attribute a on
        # cd.attribute_id = a.id
        # where double_value >= 160 and a.attribute_value = 'result_value_num';

        # query by date
        print '## comparator_date[0] is: ', comparator_date[0]
        print '## comparator_date[1] is: ', comparator_date[1]

        if comparator_date[i]:
            if comparator_date[i] == 'between':
                a[i] = a[i].filter(between(Clinical.event_date,
                                           date[0],
                                           date[1]))

                if debug:
                    print 'date bt '

            else:
                a[i] = a[i].filter(Clinical.event_date.op(comparator_date[i])([value_date[i]]))

                print '## a[i] is: ', a[i]
                print '## value_date[i] is: ', value_date[i]

                if debug:
                    print 'date other '

        # select patient_sid, lft, rgt
        # from
        # clinical_data cd inner join
        # (select attribute_value, patient_sid, lft, rgt
        # from clinical_data cd join attribute a on a.id = cd.attribute_id
        # where string_value = '13457-7' and a.attribute_value = 'test_code') ldl
        # on
        # cd.patient_sid = ldl.patient_sid
        # and
        # cd.lft >= ldl.lft
        # and
        # cd.rgt <= ldl.rgt inner join
        # attribute a on
        # cd.attribute_id = a.id
        # where double_value >= 160 and a.attribute_value = 'result_value_num'
        # and cd.event_date >= '1/1/1970';

        # construct final subquery
        a[i] = a[i].group_by(Clinical.patient_sid).subquery()

        print '## a[i] (final subquery) is: ', a[i]

    else:
        print 'error!'

if debug:
    print 'final atomic query'
    print a[1]
    print 'query key for join:'
    #print a[1].c.patient_sid

    #return a[1]