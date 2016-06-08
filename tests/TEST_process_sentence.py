import unittest
from parse import process_sentence



# sentence = '(((A|B)|(C&D)))'
# sentence = '((((A&B)|C)|D)&E)'
sentence = 'sex:demographics;eq;demographics;sex:sex;eq;M'
# sentence = '(~(~sex:demographics;eq;demographics;sex:sex;eq;M |sex:demographics;eq;demographics;sex:sex;eq;M))' #/ Check this test case again
# sentence = '(sex:demographics;eq;demographics;sex:sex;eq;M|lab:test_code;eq;13457-7;lab:result_value_num;ge;160)'
# sentence = '(A&B)'
# sentence = ''



class MyTest(unittest.TestCase):
    def test_process_sentence(self):
        self.assertNotEqual(process_sentence(sentence), None)
        # self.assertEqual(evaluate_tree(pTree, 0), pTree.getRootVal())

unittest.main()


