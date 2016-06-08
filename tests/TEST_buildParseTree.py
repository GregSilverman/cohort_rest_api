__author__ = 'bhavtosh'


import unittest
import parse
from pythonds.basic.stack import Stack
from pythonds.trees.binaryTree import BinaryTree



fpexp = '( ( ( ( A & B ) | C ) | D ) & E ) '

#def buildParseTree(fpexp):
fplist = fpexp.split()
print "## fplist is: ", fplist
pStack = Stack()
print "## pStack is: ", pStack

eTree = BinaryTree('')
print "## eTree is: ", eTree
pStack.push(eTree)


print "## pStack.items is: ", pStack.items
currentTree = eTree
print "## currentTree is: ", currentTree
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



# Test code:
# class MyTest(unittest.TestCase):
#     def test_buildParseTree(self):
#         self.assertEqual(buildParseTree(), )


