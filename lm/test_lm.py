#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import lm

class Test_Language_Model(unittest.TestCase):

    def setUp(self):
        print "Testing the LM"
        self.test_sen = [ "A", "quick", "brown", "fox" ]
        self.wrong_sen = ["fox", "quick", "a", "brown" ]

    def test_lm(self):
        print "Testing the LM"
        print "Score of: %s = %f " % (str(self.test_sen), lm.get_lm_score(self.test_sen))
        print "Score of: %s = %f " % (str(self.wrong_sen), lm.get_lm_score(self.wrong_sen))
        #lm.get_lm_score(self.wrong_sen)
        self.assertTrue(lm.get_lm_score(self.test_sen) > lm.get_lm_score(self.wrong_sen), "A proper English string should get a higher score than a garbled one")

if __name__ == '__main__':
    unittest.main()

