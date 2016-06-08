import tempfile
import os
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import pandas as pd
import time as t

# complement result sets for output
def list_complement(result_right, result_left, results):

    if result_left and result_right:

        # must be SQLAlchemy query object if not list
        if type(result_left) is not list:
            left = pd.read_sql(result_left.statement, result_left.session.bind)
        else:
            left = pd.DataFrame(result_left)

        if type(result_right) is not list:
            right = pd.read_sql(result_right.statement, result_right.session.bind)
        else:
            right = pd.DataFrame(result_right)

        #start = t.time()
        # find complement where items in left not in right
        #frames = left[~left.sid.isin(right.sid)]

        r_sid = set(right.sid)
        left.set_index('sid', inplace=True)

        frames = left.ix[~left.index.isin(r_sid)]
        frames.reset_index(level=0, inplace=True)

        # convert back to list of dictionaries
        if len(frames.index) > 0:
            test = frames.drop_duplicates().to_dict(orient='records') #sort_values(['sid','attribute'])
        else:
            test = []

        if test == []:
            test.append({'sid':0,
                         'value_s': 'null',
                         'value_d': 0,
                         'attribute': 'null'})

        #elapsed = (t.time() - start)

        #print '~~~~~~'
        #print elapsed

        return test

    else:
        del results[:]
        return []


def list_dedup(set):
    out = pd.DataFrame(set)

    # TODO: test for empty
    test = out.drop_duplicates().to_dict(orient='records')

    return test


# combine result sets for output
def list_join(result_right, result_left, results):
    # convert list of dictionaries to data frames

    if result_left and result_right:

        # must be SQLAlchemy query object if not list
        if type(result_left) is not list:
            left = pd.read_sql(result_left.statement, result_left.session.bind)
        else:
            left = pd.DataFrame(result_left)

        if type(result_right) is not list:
            right = pd.read_sql(result_right.statement, result_right.session.bind)
        else:
            right = pd.DataFrame(result_right)

        #right = pd.read_sql(result_right.statement, result_right.session.bind) #pd.DataFrame(result_right)
        #left = pd.read_sql(result_left.statement, result_left.session.bind) #pd.DataFrame(result_left)

        start = t.time()
        # get matches
        #matches_right = right[right.sid.isin(left.sid)]
        #matches_left = left[left.sid.isin(right.sid)]

        r_sid = set(right.sid)
        l_sid = set(left.sid)

        left.set_index('sid', inplace=True)
        right.set_index('sid', inplace=True)

        matches_left = left.ix[left.index.isin(r_sid)]
        matches_right = right.ix[right.index.isin(l_sid)]

        matches_left.reset_index(level=0, inplace=True)
        matches_right.reset_index(level=0, inplace=True)

        # see http://stackoverflow.com/questions/22485375/efficiently-select-rows-that-match-one-of-several-values-in-pandas-dataframe

        # m = len(right)
        # n = len(left)
        #
        # if m > n:
        #     N = m
        # elif n > m:
        #     N = n
        # else: N = m

        #print 'N'
        #print n, m
        #print N
        #N = 10000

        #idx_left = np.zeros(N, dtype='bool'); idx_left[left['sid'].values] = True; right[idx_left[right['sid'].values]]
        #idx_right = np.zeros(N, dtype='bool'); idx_right[right['sid'].values] = True; left[idx_right[left['sid'].values]]

        #test_left = right[idx_left[right['sid'].values]]
        #test_right = left[idx_right[left['sid'].values]]

        frames = [matches_right, matches_left]

        #frames = [test_right, test_left]

        if len(matches_right.index) > 0 and len(matches_left) > 0:
            # convert back to list of dictionaries
            test = pd.concat(frames).drop_duplicates().to_dict(orient='records') #sort_values(['sid','attribute'])
        else:
            test = []

        elapsed = (t.time() - start)

        #print '&&&&&'
        #print elapsed

        # empty set
        if test == []:
            test.append({'sid':0,
                         'value_s': 'null',
                         'value_d': 0,
                         'attribute': 'null'})

        return test

    else:
        del results[:]
        return []



