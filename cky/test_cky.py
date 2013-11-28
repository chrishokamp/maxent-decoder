#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json as json
import pickle
import ipdb as ipdb

import segment_phrases.segment_phrases as seg
import cky as cky
import phrase_table.DB_Phrase_Table as DB_Phrase_Table
from pprint import pprint

#for tests -- TODO: segmentation is dangerous
import preprocess.tokenizer as tokenizer

# STEPS:
#   tokenize a sentence
#   get all of its phrases
#   put them into their place in the phrase table
#   THEN:
#   fill the table -- INCLUDING CELLS in upper tiers which already have lexical rule applications
#       - for upper rows, the lexical rule is just another option in that cell

class TestCKY(unittest.TestCase):

    # setup -- create a new CKY instance
    def setUp(self):

        #TEST SENTENCE BUFFER
        # test_sen = [ "Akteure", "haben", "Aktien" ]
        # test_sen = [ "ist", "nicht", "gekommen" ]
        # test_sen = [ "aber", "das", "ist", "nicht" ]

        #TODO: this one makes tests fail: test_sen = [ "er", "ist", "aber", "super", "klug" ]
        #test_sen = [ "er", "ist", "wirklich", "sehr", "klug" ]
        #TODO: this one has unknown token(s) --> Frauenquote
        # test_sen = [ "Die", "gesetzliche", "Frauenquote", "beschleunigt", "den", "Wandel", "in", "deutschen", "Konzernen", "." ]

        #test_sen = [ "Die", "Frau", "ist", "wirklich", "sehr", "klug" ]
        #test_sen = [ "Der", "Direktor", "bedankte", "sich", "bei", "die", "Frau", "." ]
        #test_sen = [ "Ich", "habe", "mich", "in", "ihn", "verliebt", "." ]
        #test_sen = [ "Meine", "Kinder", "haben", "Schreiben", "gelernt", "." ]
        #test_sen = [ "Das", "Programm", "wird", "zum", "ersten", "Testfall", "." ]

        #TODO: this throws an error because of character encodings -- "für"
        #test_sen = [ "Das", "Programm", "für", "die", "Europawahl", "wird", "zum", "ersten", "Testfall", "." ]

        # test_sen = tokenizer.tokenize("Meine Kinder haben Schreiben gelernt." )
        #test_sen = tokenizer.tokenize("Ich liebe dich" )
        #test_sen = tokenizer.tokenize("Er kennt mich aus der Schule." )
        test_sen = tokenizer.tokenize("Ich kenne dich" )
        # END TEST SENTENCE BUFFER

        self.test_sen = test_sen
        sentence_phrases = seg.all_phrases(test_sen, len(test_sen))
        self.sentence_phrases = sentence_phrases

        #phrase_table = test_pt = pickle.load(open('../phrase_table/test_phrase_table.db','r'))
        #phrase_table = test_pt = pickle.load(open('../phrase_table/big_phrase_table.db','r'))

        # initialize the DB_Phrase_Table
        dbPT = DB_Phrase_Table.DB_Phrase_Table('../phrase_table/phrase_table_sqlite.db')
        self.dbPT = dbPT
        self.cky_parser = cky.CKY(sentence_phrases, dbPT)

    def test_initialize_table(self):
        initial_parse_table = self.cky_parser.parse_table
        phrases = self.sentence_phrases
        sen_length = len(phrases[0])
        for index,l in enumerate(phrases):
            for i, j, p in zip(range(1, len(l)+1), range(index+1, sen_length+1), l):
                phrase = " ".join(p)
                #print "CURRENT PHRASE IS: %s" % phrase
                if self.dbPT.get_all_matches((phrase,)):
                    #print self.dbPT.get_all_matches((phrase,))
                    self.assertTrue(len(initial_parse_table[(i,j)]) > 0, "if DB contains a derivation for (i,j), then i,j should not be empty in the DB")

    # I want to see what each of the derivation objects looks like
    def test_derivation_objects(self):
        initial_parse_table = self.cky_parser.parse_table
        phrases = self.sentence_phrases
        sen_length = len(phrases[0])
        for index,l in enumerate(phrases):
            for i, j, p in zip(range(1, len(l)+1), range(index+1, sen_length+1), l):
                phrase = " ".join(p)
                #print "CURRENT PHRASE IS: %s" % phrase
                if self.dbPT.get_all_matches((phrase,)) is not None:
                    derivations = initial_parse_table[(i,j)]
                    for d in derivations:
                        #print "HERE IS A DERIVATION OBJECT: "
                        #print d.toString()
                        pass

    def test_decode(self):
        self.cky_parser.decode()

    # TODO: doesn't test anything!
    def test_lexical_rule(self):
        phrase = " ".join(["er", "ist"])
        #print "\n\nCURRENT PHRASE IS: %s" % phrase
        db_phrases = self.dbPT.get_all_matches((phrase,))
        if db_phrases is not None:
            for english_phrase in db_phrases:
                #print "\tENGLISH PHRASE IS: %s" % english_phrase['target']
                lex_rule_score = self.cky_parser.apply_lexical_rule(english_phrase)
                #print "LEXICAL RULE SCORE: "
                #print "\t\t" + str(lex_rule_score)

#    # TODO: parser needs to point to the cell AND the symbol that generated it in that cell
#    def test_return_all_derivations(self):
#        # for each S in [0, len(S)], follow backpointers recursively to get all derivations with this S as root
#        s = "Book the flight through Houston"
#        toks = self.cky_parser.preprocess(s)
#        lexical_map = self.cky_parser.words_to_units(self.grammar["lexicon"])
#        rule_map = self.cky_parser.rule_map(self.grammar["rules"])
#
#        # parse_table is in the outer scope?
#        parse_table = self.cky_parser.parse(toks, lexical_map, rule_map)
#        s_labels = [ x["source"] for x in filter(lambda x: x["label"] == "S", parse_table[(0,5)]) ]
#        S_list = [ x for x in filter(lambda x: x["label"] == "S", parse_table[(0,5)]) ]
#
#        # TODO: cell is currently a list! --> solution -- index of the symbol in the list
#        # INSIGHT: S isn't a list, so we can start there
#        def derivations(cell):
#            #pprint("the type of this cell is: %s" % type(cell))
#
#            if cell["source"] == "leaf":
#                leaf_cell = defaultdict()
#                leaf_cell["sym"] = cell["label"]
#                leaf_cell["L"] = {}
#                leaf_cell["R"] = {}
#                print "returning cell: %s" % json.dumps(leaf_cell)
#                return leaf_cell
#
#            # TODO: HACK! --> the keys should point to lists
#            # get the symbols of L and R
#            # the int index tells us which symbol in the list
#            L_sym = cell["source"]["L_sym"]
#
#            R_sym = cell["source"]["R_sym"]
#
#            # find the L_sym and R_sym cells: TODO - can there be more than one parse with the same symbol?
#            #   - working answer - probably yes in some cases - a cell just represents a span
#            # we need a number index to the right symbol - actually we need to add all derivations with the same symbol
#
#            # get the correct left and right sides of this cell (indexed by nonterm)
#            L_map = {x["label"]:x for x in parse_table[cell["source"]["index"][0]]}
#            #L_map = defaultdict(list)
#            #R_map = defaultdict(list)
#            #for x in parse_table[cell["source"]["index"][0]]:
#            #    L_map[x["label"]].append(x)
#
#            # L = L_map[L_sym][L_index]
#            L = L_map[L_sym]
#            R_map = {x["label"]:x for x in parse_table[cell["source"]["index"][1]]}
#            #for x in parse_table[cell["source"]["index"][1]]:
#            #    R_map[x["label"]].append(x)
#
#            #R = R_map[R_sym][R_index]
#            R = R_map[R_sym]
#            #TODO: push all equivalent nodes onto the list which represents equivalent derivations at this level
#            # END HACK
#
#            # TODO: doesn't handle multiple derivations of the same symbol
#            node = util.makehash()
#            node["sym"] = cell["label"]
#            node["L"] = derivations(L)
#            node["R"] = derivations(R)
#
#            print "returning cell: %s" % json.dumps(node, sort_keys=True, indent=4, separators=(',', ': '))
#
#            #return node
#            return node
#
#        # each derivation is a different tree
#        derivation_list = [ derivations(x) for x in S_list ]
#
#        #TODO: test
#        #derivation_list = derivations(S_list[0])
#        for i, derivation in enumerate(derivation_list):
#            print "\nNOW PRINTING DERIVATION LIST %i: \n" % (i)
#            print "returning cell: %s" % json.dumps(derivation, sort_keys=True, indent=4, separators=(',', ': '))
#        #print derivation_list
#        #json.dumps(derivation_list)
#
#        # Working Notes:
#        # recursive function: base case is no pointer to L and R contexts
#        # derivations are pairs of tuples
#        # Object format:
#        # {
#        #    sym:
#        #    L:
#        #    R:
#        # }
#
#
#
if __name__ == '__main__':
    unittest.main()
