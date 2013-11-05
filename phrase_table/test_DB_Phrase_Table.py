#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import ipdb as ipdb
from pprint import pprint

import sqlite3
import DB_Phrase_Table

print "inside DB_Phrase_Table"

class TestDBPhraseTable(unittest.TestCase):

    # setup -- load the database
    # the table 'phrases' was made with the following command:
    # c.execute('''CREATE TABLE phrases (source text, target text, fe real, lex_fe real, ef real, lex_ef real)''')
    def setUp(self):
        print "setting up..."
        self.dbPT = DB_Phrase_Table.DB_Phrase_Table('phrase_table_sqlite.db')

    def test_get_all_matches(self):
        all_matches = self.dbPT.get_all_matches(('Ansicht',))
        self.assertGreater(len(all_matches), 1, "The word 'Ansicht' should have more that one match in the db_phrase_table")
        print "PRINTING ALL MATCHES"
        print all_matches


    def test_row_factory(self):
        # do the query
        self.dbPT.select_with_cursor(('ziemlich',))
        # grab a result
        a_match = self.dbPT.c.fetchone()
        print "PRINTING a_match['target']"
        print a_match['target']

        self.assertTrue(a_match['target'] is not None, "We should be able to query rows using dict syntax")

if __name__ == '__main__':
    unittest.main()

