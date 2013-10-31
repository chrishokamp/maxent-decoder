#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
import ipdb as ipdb

import segment_phrases

class TestPhraseSegmentation(unittest.TestCase):

    # setup -- create a new CKY instance
    def setUp(self):
        s = ["Sample", "sentences", "are", "always", "really", "dumb", "."]
        self.phrases = segment_phrases.all_phrases(s, len(s))
        #print self.phrases

    def test_phrases(self):
        phrases = self.phrases
        len_list = [len(x) for x in phrases]
        self.assertListEqual(len_list, [7,6,5,4,3,2], "The lists of phrases should be the right size")

if __name__ == '__main__':
    unittest.main()
