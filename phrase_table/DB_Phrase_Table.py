#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

# db name is phrase_table_sqlite.db --> table name is 'phrases'
# c.execute('''CREATE TABLE phrases (source text, target text, fe real, lex_fe real, ef real, lex_ef real)''')

class DB_Phrase_Table:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    # TODO: this throws an error when the source string contains special chars! fix ASAP
    # TODO: we also can't handle unknown tokens!
    def get_all_matches(self, source_string):
        self.c.execute('SELECT * FROM phrases WHERE source=?', source_string)
        all_matches = self.c.fetchall()
        # TODO: quick hack to constrain match size
        if all_matches:
            all_matches = sorted(all_matches, key=lambda d: d['ef'])[::-1][:20]
        return all_matches

    def select_with_cursor(self, source_string):
        self.c.execute('SELECT * FROM phrases WHERE source=?', source_string)

    def disconnect(self):
        self.conn.commit()
        self.conn.close()

