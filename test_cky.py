#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
from collections import defaultdict
import ipdb as ipdb

import object_utils as util
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
        s_labels = [ x["source"]["index"] for x in filter(lambda x: x["label"] == "S", parse_table[(0,5)]) ]
        correct_labels = [((0, 1), (1, 5)), ((0, 3), (3, 5)), ((0, 3), (3, 5))]

        self.assertSetEqual(frozenset(s_labels), frozenset(correct_labels), "The parser should find three sentences at (0, num_tokens)")
        #pprint(parse_table)

    # TODO: parser needs to point to the cell AND the symbol that generated it in that cell
    def test_return_all_derivations(self):
        # for each S in [0, len(S)], follow backpointers recursively to get all derivations with this S as root
        s = "Book the flight through Houston"
        toks = self.cky_parser.preprocess(s)
        lexical_map = self.cky_parser.words_to_units(self.grammar["lexicon"])
        rule_map = self.cky_parser.rule_map(self.grammar["rules"])

        # parse_table is in the outer scope?
        parse_table = self.cky_parser.parse(toks, lexical_map, rule_map)
        s_labels = [ x["source"] for x in filter(lambda x: x["label"] == "S", parse_table[(0,5)]) ]
        S_list = [ x for x in filter(lambda x: x["label"] == "S", parse_table[(0,5)]) ]

        # TODO: cell is currently a list! --> solution -- index of the symbol in the list
        # INSIGHT: S isn't a list, so we can start there
        def derivations(cell):
            #pprint("the type of this cell is: %s" % type(cell))

            if cell["source"] == "leaf":
                leaf_cell = defaultdict()
                leaf_cell["sym"] = cell["label"]
                leaf_cell["L"] = {}
                leaf_cell["R"] = {}
                print "returning cell: %s" % json.dumps(leaf_cell)
                return leaf_cell

            # TODO: HACK! --> the keys should point to lists
            # get the symbols of L and R
            # the int index tells us which symbol in the list
            L_sym = cell["source"]["L_sym"]

            R_sym = cell["source"]["R_sym"]

            # find the L_sym and R_sym cells: TODO - can there be more than one parse with the same symbol?
            #   - working answer - probably yes in some cases - a cell just represents a span
            # we need a number index to the right symbol - actually we need to add all derivations with the same symbol

            # get the correct left and right sides of this cell (indexed by nonterm)
            L_map = {x["label"]:x for x in parse_table[cell["source"]["index"][0]]}
            #L_map = defaultdict(list)
            #R_map = defaultdict(list)
            #for x in parse_table[cell["source"]["index"][0]]:
            #    L_map[x["label"]].append(x)

            # L = L_map[L_sym][L_index]
            L = L_map[L_sym]
            R_map = {x["label"]:x for x in parse_table[cell["source"]["index"][1]]}
            #for x in parse_table[cell["source"]["index"][1]]:
            #    R_map[x["label"]].append(x)

            #R = R_map[R_sym][R_index]
            R = R_map[R_sym]
            #TODO: push all equivalent nodes onto the list which represents equivalent derivations at this level
            # END HACK

            # TODO: doesn't handle multiple derivations of the same symbol
            node = util.makehash()
            node["sym"] = cell["label"]
            node["L"] = derivations(L)
            node["R"] = derivations(R)

            print "returning cell: %s" % json.dumps(node, sort_keys=True, indent=4, separators=(',', ': '))

            #return node
            return node

        # each derivation is a different tree
        derivation_list = [ derivations(x) for x in S_list ]

        #TODO: test
        #derivation_list = derivations(S_list[0])
        for i, derivation in enumerate(derivation_list):
            print "\nNOW PRINTING DERIVATION LIST %i: \n" % (i)
            print "returning cell: %s" % json.dumps(derivation, sort_keys=True, indent=4, separators=(',', ': '))
        #print derivation_list
        #json.dumps(derivation_list)

        # Working Notes:
        # recursive function: base case is no pointer to L and R contexts
        # derivations are pairs of tuples
        # Object format:
        # {
        #    sym:
        #    L:
        #    R:
        # }



if __name__ == '__main__':
    unittest.main()
