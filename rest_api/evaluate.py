#!/usr/bin/env python
from gevent import monkey
monkey.patch_all()
from pythonds.basic.stack import Stack
from pythonds.trees.binaryTree import BinaryTree
import sqla_methods
import set_operations as so
import gevent

from build_atom import parse_atomic_particles

debug = False

"""
Incoming Boolean sentences - molecules - are parsed into a binary tree.

Test expressions to parse:

sentence = '((((A&B)|C)|D)&E)'

sentence = '(E&(D|(C|(A&B))))'

sentence = '(((A|(B&C))|(D&(E&F)))|(H&I))'

"""

# build parse tree from passed sentence
# using grammatical rules of Boolean logic
def buildParseTree(fpexp):
    fplist = fpexp.split()
    pStack = Stack()
    eTree = BinaryTree('')
    pStack.push(eTree)
    currentTree = eTree

    for i in fplist:

        if i == '(':
            currentTree.insertLeft('')
            pStack.push(currentTree)
            currentTree = currentTree.getLeftChild()
        elif i not in ['&', '|', '&~', '|~', ')']:
            currentTree.setRootVal(i)
            parent = pStack.pop()
            currentTree = parent
        elif i in ['&', '|', '&~', '|~']:
            currentTree.setRootVal(i)
            currentTree.insertRight('')
            pStack.push(currentTree)
            currentTree = currentTree.getRightChild()
        elif i == ')':
            currentTree = pStack.pop()
        else:
            raise ValueError

    return eTree


def process_sentence(sentence):

    # prepare statement for case when a boolean AND/OR is given
    n_and = sentence.count('&')
    n_or = sentence.count('|')

    if (n_and + n_or) > 0 and (n_and > 0 or n_or > 0):
        sentence = sentence.replace('(', ' ( '). \
            replace(')', ' ) '). \
            replace('&', ' & '). \
            replace('|', ' | '). \
            replace('~', ' ~ '). \
            replace('&  ~', '&~'). \
            replace('|  ~', '|~'). \
            replace('  ', ' ')

    if debug:
        print sentence

    pt = buildParseTree(sentence)

    # print out parse tree nodes
    #pt.postorder()

    results = [] # used to construct record set for output via Ajax response

    if '~' in sentence:
        # entire population for calculating complement
        all_out = sqla_methods.get_list(sqla_methods.get_query())

    # recursively build boolean result list object using parse tree
    def evaluate_tree(tree):

        if tree:
            # parallelism: http://stackoverflow.com/questions/17038288/nested-parallelism-in-python

            left_child = gevent.spawn(evaluate_tree, tree.getLeftChild())
            right_child = gevent.spawn(evaluate_tree, tree.getRightChild())

            if left_child.get() and right_child.get():
                # initialize query object for use in constructing new leaf
                # from evaluation of current nodes
                query = []

                # string is a query object built from an atomic query string
                if type(left_child.get()) is str:
                    # build atomic query for evaluation to get result set
                    left_atom, whole, print_all = parse_atomic_particles(left_child.get())
                    # get query object
                    left_out = sqla_methods.get_query('left', left_atom)

                    # test for existence
                    print 'test'
                    sqla_methods.check_exists(left_child.get())

                    # write to memoize
                    sqla_methods.add_record(str(sentence), str(results))

                # list of dictionaries is a computed record set
                elif type(left_child.get()) is list:
                    # left child was a built list of dictionaries
                    left_out = left_child.get()

                if type(right_child.get()) is str:
                    right_atom, whole, print_all = parse_atomic_particles(right_child.get())
                    right_out = sqla_methods.get_query('right', right_atom)

                    # test for existence
                    print 'test'
                    sqla_methods.check_exists(right_child.get())

                    # write to memoize
                    sqla_methods.add_record(str(sentence), str(results))

                elif type(right_child.get()) is list:
                    right_out = right_child.get()

                # negation
                if tree.getRootVal() == '&~' or tree.getRootVal() == '|~':
                    # result set of all sids in all_out that are not in right_out
                    complement = so.list_complement(right_out, all_out, results)

                # case boolean AND/AND NOT
                if tree.getRootVal() == '&' or tree.getRootVal() == '&~':
                    if tree.getRootVal() == '&':
                        # concat output for matching sids -> intersect
                        join_out = so.list_join(right_out, left_out, results)

                    elif tree.getRootVal() == '&~':
                        join_out = so.list_join(complement, left_out, results)
                        del results[:]

                    if results and tree.getRootVal() != '&~':
                        # concat output with results on matching sids
                        out = so.list_join(join_out, results, results)

                        # clear results
                        del results[:]
                        # append clean results set
                        results.extend(out)

                    else:
                        results.extend(join_out)

                    query.extend(join_out)

                # case boolean OR/OR NOT
                elif tree.getRootVal() == '|' or tree.getRootVal() == '|~':
                    if tree.getRootVal() == '|':
                        # concat output for all sids -> union

                        # SQLAlchemy query object if not list
                        if type(right_out) is not list:
                            right_out = sqla_methods.get_list(right_out)

                        results.extend(right_out)
                        query.extend(right_out)

                    elif tree.getRootVal() == '|~':
                        results.extend(complement)
                        query.extend(complement)

                    if type(left_out) is not list:
                            left_out = sqla_methods.get_list(left_out)

                    results.extend(left_out)
                    query.extend(left_out)
                    so.list_dedup(results)

                return query

            # we are at a root and need to get the next operand
            else:
                return tree.getRootVal()

    # trivial case of single atom: no tree parsing necessary
    if (n_and + n_or) == 0:

        query, whole, print_all = parse_atomic_particles(sentence)

        if print_all:
            query = whole.subquery()

        out = sqla_methods.get_list(sqla_methods.get_query('trivial', query))

        results.extend(out)

        # test for existence
        test = sqla_methods.check_exists(sentence)
        #print test

        # write to memoize
        sqla_methods.add_record(str(sentence), str(results))

        return results

    # there were '&' or '|' operators, and thus we have a molecule
    elif (n_and + n_or) > 0 and (n_and > 0 or n_or > 0):

        evaluate_tree(pt)

        return results