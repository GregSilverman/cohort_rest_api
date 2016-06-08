__author__ = 'bhavtosh'


from app import db, app, models
from sqlalchemy.sql import label, distinct, and_, text, or_, union_all, select, exists

import unittest
from parse import parse_atomic_particles, buildParseTree
import sqlalchemy

Clinical = models.ClinicalData

debug = False
Attribute = models.Attribute
debug = False

operand = []  # list of operands
build = []  # simulated recursive query build steps

# sentence = '(((A|B)|(C&D)))'
# sentence = '((((A&B)|C)|D)&E)'
sentence = 'sex:demographics;eq;demographics;sex:sex;eq;M'
# sentence = '(~(~sex:demographics;eq;demographics;sex:sex;eq;M |sex:demographics;eq;demographics;sex:sex;eq;M))' #/ Check this test case again
# sentence = '(sex:demographics;eq;demographics;sex:sex;eq;M|lab:test_code;eq;13457-7;lab:result_value_num;ge;160)'
# sentence = '((((((sex:demographics;eq;demographics;sex:sex;eq;f|sex:demographics;eq;demographics;sex:sex;eq;f)' \
#             '|sex:demographics;eq;demographics;sex:sex;eq;f)|sex:demographics;eq;demographics;sex:sex;eq;f)|' \
#             'sex:demographics;eq;demographics;sex:sex;eq;f)|((((sex:demographics;eq;demographics;sex:sex;eq;f&sex:demographics;eq;demographics;sex:sex;eq;f)' \
#             '&sex:demographics;eq;demographics;sex:sex;eq;f)&sex:demographics;eq;demographics;sex:sex;eq;f)&sex:demographics;eq;demographics;sex:sex;eq;f))|' \
#             '((((sex:demographics;eq;demographics;sex:sex;eq;f&sex:demographics;eq;demographics;sex:sex;eq;f)&' \
#             'sex:demographics;eq;demographics;sex:sex;eq;f)&sex:demographics;eq;demographics;sex:sex;eq;f)&sex:demographics;eq;demographics;sex:sex;eq;f))'
# sentence = '(A&B)'
# sentence = 'abc'



n_and = sentence.count('&')
n_or = sentence.count('|')
n_not = sentence.count('~')
i = n_and + n_or + n_not


if i > 0 and (n_and > 0 or n_or > 0):
        sentence = sentence.replace('(', ' ( '). \
            replace(')', ' ) '). \
            replace('&', ' & '). \
            replace('|', ' | '). \
            replace('~', ' ~ '). \
            replace('&  ~', '&~'). \
            replace('|  ~', '|~'). \
            replace('  ', ' ')

pTree = buildParseTree(sentence)

## --METHOD DEFINITION--

def evaluate_tree(tree, n):

        if tree:
            n += 1

            left_child = evaluate_tree(tree.getLeftChild(), n)
            right_child = evaluate_tree(tree.getRightChild(), n)

            # children contain either URL atomic payload,
            # or iterable built SQLA query molecules

            if left_child and right_child:

                # what is list length
                j = len(operand)

                if j == 0: # grab first left child to initialize query object
                    build.append('initObject:(' + str(left_child) + ')')

                # write operand to list
                operand.append(tree.getRootVal())


                # NB: for negation we use operators &~ and |~ respectively

                whole = db.session.query(label('sid',
                                               distinct(Clinical.patient_sid)))

                # left child is a parse URL atomic query str
                if type(left_child) is str and ':' in left_child:
                    # build SQLA atomic query on basic atomic query string
                    left_atom = parse_atomic_particles(left_child)


                # right child is a parse URL atomic query str
                if type(right_child) is str and ':' in right_child:
                    right_atom = parse_atomic_particles(str(right_child))


                if tree.getRootVal() == '&~' or tree.getRootVal() == '|~':
                    # case string
                    if type(right_child) is str:
                        right_reduced = whole.outerjoin(right_atom, right_atom.c.patient_sid == Clinical.patient_sid). \
                            filter(right_atom.c.patient_sid == None).subquery()

                    if type(right_child) is not str:

                        test = right_child.subquery()

                        right_reduced =  whole.outerjoin(test, test.c.sid == Clinical.patient_sid). \
                            filter(test.c.sid == None).subquery()


                # case boolean AND/AND NOT
                if tree.getRootVal() == '&' or tree.getRootVal() == '&~':


                    if tree.getRootVal() == '&':
                        # case A&B, both children nodes are parsed URL atomic query strings
                        if type(left_child) is str and type(right_child) is str:
                            query = db.session.query(label('sid',
                                                           distinct(left_atom.c.patient_sid)))

                            query = query.join(right_atom,
                                               left_atom.c.patient_sid == right_atom.c.patient_sid)


                        # case A&B, left child is a parsed URL atomic query string, right is a build molecular query object
                        elif type(left_child) is str and type(right_child) is not str:

                            intersect = db.session.query(label('sid', distinct(left_atom.c.patient_sid)))
                            test = right_child.subquery()

                            query = intersect.join(test, left_atom.c.patient_sid == test.c.sid)


                        # left child is an iterable SQL query molecule
                        elif type(left_child) is not str and type(right_child) is str:

                            intersect = db.session.query(label('sid', distinct(right_atom.c.patient_sid)))
                            test = left_child.subquery()

                            query = intersect.join(test, right_atom.c.patient_sid == test.c.sid)


                        # both children are iterable SQL query molecules
                        elif type(left_child) is not str and type(right_child) is not str:

                            intersect = left_child.subquery()
                            test = right_child.subquery()

                            # need to build iterable query
                            query = db.session.query(label('sid', distinct(intersect.c.sid)))
                            query = query.join(test, intersect.c.sid == test.c.sid)


                    elif tree.getRootVal() == '&~':
                        # case A&~B, both children nodes are parsed URL atomic query strings
                        if type(left_child) is str and type(right_child) is str:
                            query = db.session.query(label('sid',
                                                           distinct(left_atom.c.patient_sid)))

                            query = query.join(right_reduced,
                                               left_atom.c.patient_sid == right_reduced.c.sid)


                        # case A&B, left child is a parsed URL atomic query string, right is a build molecular query object
                        elif type(left_child) is str and type(right_child) is not str:

                            intersect = db.session.query(label('sid', distinct(left_atom.c.patient_sid)))
                            query = intersect.join(right_reduced, left_atom.c.patient_sid == right_reduced.c.sid)


                        # left child is an iterable SQL query molecule
                        elif type(left_child) is not str and type(right_child) is str:

                            intersect = db.session.query(label('sid', distinct(right_reduced.c.sid)))
                            test = left_child.subquery()
                            query = intersect.join(test, right_reduced.c.sid == test.c.sid)


                        # both children are iterable SQL query molecules
                        elif type(left_child) is not str and type(right_child) is not str:

                            intersect = left_child.subquery()

                            # need to build iterable query
                            query = db.session.query(label('sid', distinct(intersect.c.sid)))
                            # perform join
                            query = query.join(right_reduced, intersect.c.sid == right_reduced.c.sid)


                # case boolean OR/OR NOT
                elif tree.getRootVal() == '|' or tree.getRootVal() == '|~':


                    if tree.getRootVal() == '|':
                        # case A|B, left and right children areparsed URL atomic query string
                        if type(left_child) is str and type(right_child) is str: # and '~' not in left_child:
                            query = db.session.query(label('sid', distinct(left_atom.c.patient_sid)))
                            union = db.session.query(label('sid', distinct(right_atom.c.patient_sid)))
                            query = query.union(union)


                        # case A|(B), left child is a parsed URL atomic query string, right is a build molecular query object
                        elif type(left_child) is str and type(right_child) is not str: # and '~' not in left_child:

                            test = right_child.subquery()

                            query = db.session.query(label('sid', distinct(test.c.sid)))
                            union = db.session.query(label('sid', distinct(left_atom.c.patient_sid)))
                            query = query.union(union)


                        # case (A)|~B, left child is a build molecular query object, right child is a parsed URL atomic query string
                        elif type(left_child) is not str and type(right_child) is str:


                            test = left_child.subquery()


                            query = db.session.query(label('sid', distinct(test.c.sid)))
                            union = db.session.query(label('sid', distinct(right_atom.c.patient_sid)))
                            query = query.union(union)


                        # case (A)|~(B), left and right children are a built molecular query object
                        elif type(left_child) is not str and type(right_child) is not str:

                            test1 = left_child.subquery()
                            test2 = right_child.subquery()

                            query = db.session.query(label('sid', distinct(test1.c.sid)))
                            union = db.session.query(label('sid', distinct(test2.c.sid)))

                            query = query.union(union)


                    elif tree.getRootVal() == '|~':

                        if type(left_child) is str and type(right_child) is str: # and '~' not in left_child:
                            query = db.session.query(label('sid', distinct(left_atom.c.patient_sid)))

                            union = db.session.query(label('dis', distinct(right_reduced.c.sid)))
                            query = query.union(union)


                        elif type(left_child) is str and type(right_child) is not str: #  and '~' not in left_child:

                            query = db.session.query(label('sid', distinct(right_reduced.c.sid)))
                            union = db.session.query(label('sid', distinct(left_atom.c.patient_sid)))
                            query = query.union(union)


                        elif type(left_child) is not str and type(right_child) is str:

                            test = left_child.subquery()

                            query = db.session.query(label('sid', distinct(test.c.sid)))
                            union = db.session.query(label('sid', distinct(right_reduced.c.sid)))
                            query = query.union(union)


                        elif type(left_child) is not str and type(right_child) is not str:

                            test1 = left_child.subquery()
                            test2 = right_reduced

                            query = db.session.query(label('sid', distinct(test1.c.sid)))
                            union = db.session.query(label('sid', distinct(test2.c.sid)))

                            query = query.union(union)


                return query

            # we are at a root and need to get the next operand
            else:


                if i == 0:  # case with no operands
                    build.append(bool)
                    operand.append('initSession')


                return tree.getRootVal()


method = evaluate_tree(pTree, 2)

print 'evaluate_tree : ', evaluate_tree(pTree, 2)
print 'evaluate_tree TYPE: ', type(evaluate_tree(pTree, 2))




class MyTest(unittest.TestCase):
#     # def test_evaluate_tree_returns_anything(self):
#     #     # self.assertEqual(evaluate_tree(pTree, 1), pTree.getRootVal())
#     #     self.assertNotEqual(evaluate_tree(pTree, 0), None)
#
#     def test_evaluate_tree_returns_correctObject(self):
#         # self.assertEqual(evaluate_tree(pTree, 1), pTree.getRootVal())
#         self.assertIs(type(evaluate_tree(pTree, 1)), sqlalchemy.orm.query.Query)
#         # self.assertNotEqual(evaluate_tree(pTree, 0), None)
#
    def test_evaluate_tree_testFor_baseCase(self):
        # self.assertEqual(evaluate_tree(pTree, 1), pTree.getRootVal())
        self.assertIs(type(evaluate_tree(pTree, 1)), )
        # self.assertNotEqual(evaluate_tree(pTree, 0), None)


unittest.main()
