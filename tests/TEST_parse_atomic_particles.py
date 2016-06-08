__author__ = 'bhavtosh'

'''The method takes the string, divides it into diff. components and staores in diff. lists'''

debug = False

#def parse_atomic_particles(varargs):
#varargs = '~sex:demographics;eq;demographics;sex:sex;eq;M'
varargs = 'lab:test_code;eq;13457-7;lab:result_value_num;bt;120,160,DATE,greater,2010-01-02'
# varargs = '~(~sex:demographics;eq;demographics;sex:sex;eq;M' \
#            '|sex:demographics;eq;demographics;sex:sex;eq;M)'
if debug:
    print 'varargs'
    print varargs

# delimiter between atomic query particles: key, comparator, value
# for use in splitting into particles
separator = ';'

atom = varargs

#if debug:
    #print 'number comparator separators: ' + str(n_bool) + ' with atoms:'
    #print 'of length: ' + str(len(atoms))
    #print 'atoms'
    #print atoms[0]

# initialize lists
a = []  # list element for returned atoms

#print '##1', a

for i in range(0, 1):
    a.append('')

#print '##2', a

for j in range(0, 1):

    # initialize query components
    particles = atom.split(separator, 6)  # atom consists of 6 query components to be parsed, aka particles
    key = []  # array of key buckets/attributes
    comparator = []  # array of comparators
    value = []  # array of values
    comparator_date = []  # array of date comparators
    value_date = []  # array of date components
    neg = []  # negation; TODO, handle in a more generalized way



    #print '##3', particles

    # TODO: implement as a dictionary
    for i in range(len(particles)):

        particle = particles[i]
        #print '##4', particle

        # Idea is that each atomic unit consists of 6 "particles" delimited by a ';',
        # where each particle consists of a:
        #
        # -> key: representing a bucket name by an attribute
        # -> comparator: representing the logical operation to perform, NB: for bucket this should always be 'eq'
        # -> value: name of bucket
        # -> key: representing an item within the bucket to query by attribute name
        # -> comparator: representing the logical operation to perform on given attribute compared to given value
        # -> value: attribute item's value for comparison

        # map particle components to appropriate lists
        if '~' in particle:
            neg.append('~')
        if ':' in particle:
            e = particle.split(':')
            #if debug:
            #print '## bucket:attribute -> ' + str(e[1])  # we found the bucket filter
            #print '## e is: ', e
            key.append(str(e[1]))
            #print '## key is: ', key
        elif 'eq' in particle:  # look for the comparators
            if debug:
                print '=='
            comparator.append('=')
        elif 'lt' in particle:
            if debug:
                print '<'
            comparator.append('<')
        elif 'le' in particle:
            if debug:
                print '<='
            comparator.append('<=')
        elif 'gt' in particle:
            if debug:
                print '>'
            comparator.append('>')
        elif 'ge' in particle:
            if debug:
                print '>='
            comparator.append('>=')
        elif 'ne' in particle:
            if debug:
                print '!='
            comparator.append('!=')
        elif 'in' in particle:
            if debug:
                print 'in'
            comparator.append('in')
        elif 'bt' in particle:
            if debug:
                print 'bt'
            comparator.append('between')
        else:  # has to be value
            #if debug:
            #print 'vals: ' + particle

            # if DATE component is not part of value particle we use epoch date as default
            if not 'DATE' in particle:
                # pad date to fill array
                comparator_date.append('>')
                value_date.append('1970-01-01')
                value.append(particle)

                #print '## value_date is:', value_date
            # DATE is part of value particle, so we use it
            elif 'DATE' in particle:
                # split value particle into value and date components
                date_stuff = particle.split(',DATE,')

                #print '## date_stuff is:', date_stuff
                # grab non date value part of list for attribute comparison
                value.append(date_stuff[0])

                #print '## comparator_date is:', comparator_date

                # grab operator for date comparison from list
                if 'greater' in date_stuff[1]:
                    comparator_date.append('>')
                    #print '## comparator_date is:', comparator_date
                elif 'less' in date_stuff[1]:
                    comparator_date.append('<')
                elif 'between' in date_stuff[1]:
                    comparator_date.append('between')

                #print '## comparator_date is:', comparator_date

                #print '## date_stuff is:', date_stuff[1]

                # get dates from list for comparison,
                # splitting in the case that a between comparison is given
                date = date_stuff[1].split(',')
                #print '## date is:', date

                # determine if a 'between' operation is being done
                # if there are 2 elements then split list
                if len(date) == 2:
                    temp = date_stuff[1]
                    #print '## temp is:', temp

                else:
                    temp = date_stuff[1] + ',' + date_stuff[2]  # 'between' op.?

                #print '## value_date is:', value_date
                value_date.append(temp)
                #print '## value_date is:', value_date

                print '## key:', key
                print '## comparator:', comparator
                print '## value: ', value
                print '## comparator_date: ', comparator_date
                print '## value_date: ', value_date
                print '## neg: ', neg


                if debug:
                    print 'iterated comparator_date: '
                    print comparator_date
                    print 'iterated value_date: '
                    print value_date

    if debug:
        print 'comparator: '
        print comparator
        print 'value: '
        print value
        print 'key: '
        print key
        print 'j:' + str(j)
        print 'comparator_date, value_date ->'
        print comparator_date
        print value_date
        print 'neg'
        print neg

    #a[j] = make_atomic_query(key, comparator, value, comparator_date, value_date, neg)

    if debug:
        print 'TESTING 1... 2... 3...'
        print a[j].c.patient_sid
        print a[j]
        print str(j)

#return a[0]