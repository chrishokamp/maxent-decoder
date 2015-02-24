#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
from collections import defaultdict
import pickle
import ipdb as ipdb

import Phrase_Table
from pprint import pprint

class TestPhraseTable(unittest.TestCase):

    def setUp(self):
        lines = [line.strip() for line in open('tiny_phrase_table', 'r').readlines()]
        # the structure of the fields is: ["target", "scores", "alignment", "counts"]
        field_names = ["target","f|e","lex_f|e","e|f", "lex_e|f"]
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

    # Note: pickling won't be as efficient as sqlite3 -- check out sqlalchemy in the future
    def test_pickle_and_unpickle(self):
        phrase_table = self.PT.getTable()
        pickle.dump(phrase_table, open('test_phrase_table.db', 'w'))
        test_pt = pickle.load(open('test_phrase_table.db','r'))
        self.assertTrue(len(test_pt["Absichten"]) > 2, "Test that the field for \"Absichten\" is not empty in the unshelved object")

if __name__ == '__main__':
    unittest.main()
