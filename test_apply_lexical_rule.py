#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
from collections import defaultdict
import pickle
import ipdb as ipdb

#import apply_lexical_rule
from pprint import pprint
import segment_phrases.segment_phrases as seg

class TestLexicalRule(unittest.TestCase):

    # setup -- create a new CKY instance, a new phrase table, and a new phrase segmentation
    def setUp(self):
        test_sen = ["Sample", "sentences", "are", "always", "really", "dumb", "."]
        self.test_phrases = seg.all_phrases(test_sen, len(test_sen))
        # small map
        #self.phrase_table = pickle.load(open('phrase_table/test_phrase_table.db'))
        # big map
        self.phrase_table = pickle.load(open('phrase_table/big_phrase_table.db'))

    # this is a test of the segmenter
    def test_items_in_phrases(self):
        self.assertListEqual(self.test_phrases[5], [ ["Sample", "sentences", "are", "always", "really", "dumb"],["sentences", "are", "always", "really", "dumb", "."] ], "The top-level (2 phrase) segmentation should be correct")

    def test_phrase_mapping(self):
        # we know this sentence has some matches in the phrase table
        de_test_sen = ["Akteure", "haben", "Aktien"]
        # print the mappings for each phrase
        for i, level in enumerate(seg.all_phrases(de_test_sen,len(de_test_sen))):
            #print "FOR LEVEL: %i" % i
            for j, phrase in enumerate(level):
                 index = "[" + str(i) + ", " + str(j) + "]"
                 #print "PHRASE INDEX: %s" % index
                 #print "FOR FOREIGN PHRASE COVERAGE: %s" % phrase
                 key = " ".join(phrase) #TODO: hack? -- depends upon tokenization methods
                 # print "\tThe mappings are: %s" % str(self.phrase_table[key])
                 print "\tThe mappings are: %s" % str([(x["target"], x["e|f"]) for x in self.phrase_table[key]])

    def test_lexical_rule_application(self):
        # segments should be put in the proper spot into the table
        pass

if __name__ == '__main__':
    unittest.main()
