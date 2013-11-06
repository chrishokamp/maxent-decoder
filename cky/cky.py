#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from collections import Counter
from collections import defaultdict
import numpy as np
import phrase_table.DB_Phrase_Table
import lm.lm as lm
import preprocess.tokenizer as tokenizer
# import ipdb

#   - A CKY chart is generated for EVERY SENTENCE that we want to translate
class CKY:
    def __init__(self, sentence_phrases, db_phrase_table):
        self.dbPT = db_phrase_table
        self.parse_table = self.fill_table(sentence_phrases)

    # parsing starts by initializing the lexical rule applications that exist in our table
    # there are no rules -- any phrase can be combined, we're just looking for the top-scoring ones
    def fill_table(self, sentence_phrases):
        parse_table = defaultdict(list)
        sen_length = len(sentence_phrases[0])
        for level_index, level in enumerate(sentence_phrases):
            for i, j, phrase in zip(range(1,len(level)+1), range(level_index+1, sen_length+1), level):
                p = " ".join(phrase)
                all_matches = self.dbPT.get_all_matches((p,))
                if all_matches is not None:
                    parse_table[(i,j)] = all_matches
                    # working: calculate the score of the lexical trule for this phrase

        return parse_table

    # TODO: we need to learn weights for all of these features
    def apply_lexical_rule(self, db_row):

        # TODO: add PHRASE PENALTY, and WORD PENALTY
        fe = db_row['fe']
        ef = db_row['ef']
        lex_fe = db_row['lex_fe']
        lex_ef = db_row['lex_ef']
        # TODO: push tokenization into the DB
        lm_score = lm.get_lm_score(tokenizer.tokenize(db_row['target']))
        #features = {'fe':fe , 'ef':ef, 'lex_fe':lex_fe, 'lex_ef':lex_ef, 'lm_score':lm_score}

        lex_rule_score = np.log(fe) + np.log(ef) + np.log(lex_fe) + np.log(lex_ef) + lm_score
        return lex_rule_score

#   Parsing happens after the lexical rule has been applied
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
