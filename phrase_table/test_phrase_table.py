#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
from collections import defaultdict
import ipdb as ipdb

import Phrase_Table
from pprint import pprint

class TestPhraseTable(unittest.TestCase):

    # setup -- create a new CKY instance
    def setUp(self):
        lines = [line.strip() for line in open('tiny_phrase_table', 'r').readlines()]
        field_names = ["target", "scores", "alignment", "counts"]
        self.PT = Phrase_Table.Phrase_Table(lines, field_names)
        #print self.PT.phrase_table['Absichten']

    def test_phrase_table_entry(self):
        self.assertGreaterEqual(len(self.PT.phrase_table['Absichten']), 1, "The number of entries in the phrase table for Absichten should be >=1")

    def test_get_entry(self):
        absicht = self.PT.getEntry("Absicht")
        self.failUnless(len(self.PT.getEntry("Absicht")) > 0)

    # Note: this test depends on the entry that's being tested
    def test_that_all_keys_are_unique(self):
        s = [ k["target"] for k in self.PT.getEntry("Absichten") ]
        self.failUnless(len(s) == len(frozenset(s)))

if __name__ == '__main__':
    unittest.main()
