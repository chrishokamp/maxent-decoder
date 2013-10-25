#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque,defaultdict

class Phrase_Table:
    def __init__(self, lines, unit_names):
        self.phrase_table = self.build_phrase_table(lines, unit_names)

    def build_phrase_table(self, lines, unit_names):
        line_units = [line.split('|||') for line in lines]

        def strip_list(l):
            return deque([u.strip() for u in l])

        lists_of_units = [strip_list(x) for x in line_units]

        phrase_table = defaultdict(list)
        # assume first elem is the key
        for entry in lists_of_units:
            f_phrase = entry.popleft()
            e = { k:v for k,v in zip(unit_names, entry) }
            phrase_table[f_phrase].append(e)

        return phrase_table

    # TODO: will throw error when item isn't found
    def getEntry(self, phrase):
        return self.phrase_table[phrase]

