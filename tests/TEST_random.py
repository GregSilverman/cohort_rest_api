__author__ = 'bhavtosh'

import unittest
from parse import parse_atomic_particles, buildParseTree

# sentence = '(((A|B)|(C&D)))'
# sentence = '((((A&B)|C)|D)&E)'
# sentence = 'sex:demographics;eq;demographics;sex:sex;eq;M'
# sentence = '(~(~sex:demographics;eq;demographics;sex:sex;eq;M |sex:demographics;eq;demographics;sex:sex;eq;M))' #/ Check this test case again
# sentence = '(sex:demographics;eq;demographics;sex:sex;eq;M|lab:test_code;eq;13457-7;lab:result_value_num;ge;160)'
# sentence = '(A&B)'
sentence = ''


n_and = sentence.count('&')
n_or = sentence.count('|')
n_not = sentence.count('~')
i = n_and + n_or + n_not

print 'i: ', i

if i > 0 and (n_and > 0 or n_or > 0):
        sentence = sentence.replace('(', ' ( '). \
            replace(')', ' ) '). \
            replace('&', ' & '). \
            replace('|', ' | '). \
            replace('~', ' ~ '). \
            replace('&  ~', '&~'). \
            replace('|  ~', '|~'). \
            replace('  ', ' ')

print 'new sent: ', sentence

pTree = buildParseTree(sentence)

print 'pTree: ', pTree
print 'pTree -root: ', pTree.getRootVal()
print 'pTree -l: ', pTree.getLeftChild()
print 'pTree -r: ', pTree.getRightChild()

# test1 = parse_atomic_particles(sentence)
#
# print 'test1: ', test1


class MyTest(unittest.TestCase):
    def test_evaluate_tree(self):
        self.assertNotEqual(evaluate_tree(pTree.getRootVal(), None))