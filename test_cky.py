#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
import cky as cky
from pprint import pprint

#for tests
from nltk.tokenize import word_tokenize

class TestCKY(unittest.TestCase):

    # setup -- create a new CKY instance
    def setUp(self):
        tokenizer = word_tokenize
        self.cky_parser = cky.CKY(word_tokenize)
        self.grammar = json.loads(open("sample_cnf.json", "r").read())

    def test_empty_string(self):
        #len of empty string = 0
        d = ""
        self.assertEqual(0, len(d), "The length of the empty string should be 0")

    def test_preprocessing(self):
        #len of empty string = 0
        d = "A flight from Houston landed."
        tokenized = ["START", "a", "flight", "from", "houston", "landed"]
        self.assertListEqual(self.cky_parser.preprocess(d), tokenized, "Test that tokenization works properly")

    def test_words_to_units(self):
        lexicon = self.grammar["lexicon"]
        words_to_units = self.cky_parser.words_to_units(lexicon)
        self.assertSetEqual(frozenset(words_to_units["houston"]), frozenset(["NP", "Proper-Noun"]), "Test nonterminals for _houston_")
        self.assertSetEqual(frozenset(words_to_units["flight"]), frozenset(["Nominal","Noun"]), "Test nonterminals for _flight_")

    def test_rule_map(self):
        rules = self.grammar["rules"]
        rule_map = self.cky_parser.rule_map(rules)
        self.assertSetEqual(frozenset(rule_map[("Verb", "NP")]), frozenset(["VP", "S", "X2"]), "Tuple derivation keys should map to nonterminals")

    # first test: the parser succeeds at finding an "S" at [0, len_sentence]
    def test_parser(self):
        tokenized = ["START", "a", "flight", "from", "houston", "landed"]
        lexical_map = self.cky_parser.words_to_units(self.grammar["lexicon"])
        rule_map = self.cky_parser.rule_map(self.grammar["rules"])
        parse_table = self.cky_parser.parse(tokenized, lexical_map, rule_map)

        # test the table entries for "Houston" - NOTE: this test relies upon the order of items
        self.assertListEqual([x["label"] for x in parse_table[(3, 4)]],["NP","Proper-Noun"], "The parser should resolve words to their nonterminals")

    def test_parsing_workflow(self):
        s = "Book the flight through Houston"
        toks = self.cky_parser.preprocess(s)
        lexical_map = self.cky_parser.words_to_units(self.grammar["lexicon"])
        rule_map = self.cky_parser.rule_map(self.grammar["rules"])
        parse_table = self.cky_parser.parse(toks, lexical_map, rule_map)
        s_labels = [ x["source"] for x in filter(lambda x: x["label"] == "S", parse_table[(0,5)]) ]
        correct_labels = [((0, 1), (1, 5)), ((0, 3), (3, 5)), ((0, 3), (3, 5))]

        self.assertSetEqual(frozenset(s_labels), frozenset(correct_labels), "The parser should find three sentences at (0, num_tokens)")
        #print "\n\nFULL WORKFLOW\n"
        #pprint(parse_table)

    def test_return_all_derivations(self):
        pass

if __name__ == '__main__':
    unittest.main()
