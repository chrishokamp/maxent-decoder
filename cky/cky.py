#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from collections import Counter
from collections import defaultdict
# import ipdb
# import itertools

#   - A CKY chart is generated for EVERY SENTENCE that we want to translate
class CKY:
    def __init__(self, sentence_phrases, phrase_table):
        self.phrases = phrase_table
        self.parse_table = self.fill_table(sentence_phrases) # is this the right structure?

    # parsing CKY should start by initializing the lexical rule applications that exist in our table
    # there are no rules -- any phrase can be combined, we're just looking for the top-scoring one
    def fill_table(self, sentence_phrases):
        parse_table = defaultdict(list)
        for level in sentence_phrases:
            for i, phrase in zip(range(1,len(level)+1), level):
                p = " ".join(phrase)
                #print "i: %i, phrase: %s" % (i, p)
                if self.phrases[p] != []:
                    # TODO: update Parse Table to a faster data structure
                    parse_table[(i,i)] = self.phrases[p]

        return parse_table

    #def apply_lexical_rule(sentence_phrases):

#    def parse(self, lexical_map):
#        parse_table = defaultdict(list) # is this the right structure
#        num_columns = len(tokens)
#        for j in range(1, num_columns, 1):
#            leaf_symbols = lexical_map[tokens[j]]
#            for sym in leaf_symbols:
#                parse_table[(j-1, j)].append({"label": sym, "source": "leaf"})
#            for i in range(j-2, -1, -1):
#                for k in range(i+1, j):
#                    #ipdb.set_trace()
#                    if len(parse_table[i,k]) > 0 and len(parse_table[k,j]) > 0:
#                        B = [nonterm["label"] for nonterm in parse_table[i,k]]
#                        C = [nonterm["label"] for nonterm in parse_table[k,j]]
#                        pairs = list(itertools.product(B,C))
#                        new_derivations = []
#
#                        for pair in pairs:
#                            try:
#                                nonterms = rule_map[pair]
#                                for nonterm in nonterms:
#                                    left_symbol = pair[0]
#                                    right_symbol = pair[1]
#                                    new_derivations.append( {"label":nonterm, "source":{"index": ((i,k), (k,j)), "L_sym": left_symbol, "R_sym": right_symbol} })
#                            except KeyError:
#                                pass
#                        union = parse_table[i,j] + new_derivations
#                        parse_table[i,j] = union
#        return parse_table
#
#    def preprocess(self, sentence):
#        toks = map (lambda t: t.lower(), self.tokenizer(sentence))
#        toks.insert(0, 'START')
#        no_punct = filter(lambda word: word not in ',-.', toks)
#        return no_punct
#
#    # flip the lexicon
#    def words_to_units(self, lexicon):
#        words_to_nonterms = defaultdict(list)
#        for nonterm, wordlist in lexicon.items():
#            for word in wordlist:
#                words_to_nonterms[word].append(nonterm)
#        return words_to_nonterms
#
#    # flip the rule map --> keys are tuples (A,B)
#    def rule_map(self, rules):
#        rule_map = defaultdict(list)
#        for nonterm, derivations in rules.items():
#            for derivation in derivations:
#                rule_map[tuple(derivation)].append(nonterm)
#        return rule_map

#if __
