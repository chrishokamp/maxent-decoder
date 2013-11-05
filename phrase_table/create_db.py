#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import re
from collections import deque

phrase_table_file='filtered_phrase_table'

# create table with the proper fields
conn = sqlite3.connect('phrase_table_sqlite.db')
c = conn.cursor()
c.execute('''CREATE TABLE phrases (source text, target text, fe real, lex_fe real, ef real, lex_ef real)''')

def strip_list(l):
    return deque([u.strip() for u in l])

def insert_entry(data_row):
    c.execute('INSERT INTO phrases VALUES (?,?,?,?,?,?)', data_row)

# TODO: add parsing of moses phrase table format here
lines = [line.strip() for line in open(phrase_table_file, 'r').readlines()]

line_units = [line.split('|||') for line in lines]

lists_of_units = [strip_list(x) for x in line_units]

for entry in lists_of_units:
    f_phrase = unicode(entry.popleft(), errors='ignore')
    e_phrase = unicode(entry.popleft(), errors='ignore')
    # currently unused -- need to pop so that they don't get added to the db row
    counts = entry.pop()
    alignment = entry.pop()
    # end unused

    # split each field on whitespace except target -- there should be a name for every field
    flattened = []
    for section in entry:
        section = unicode(section, errors='ignore')
        flattened = flattened + re.split('\s+', section)
    entry_tuple = (f_phrase, e_phrase) + tuple(flattened) #TODO: hack
    insert_entry(entry_tuple)

conn.commit()
conn.close()

