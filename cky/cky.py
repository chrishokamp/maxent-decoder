#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from collections import Counter
from collections import defaultdict
import itertools
import numpy as np
import phrase_table.DB_Phrase_Table
import lm.lm as lm
import preprocess.tokenizer as tokenizer
# import ipdb

#   - A CKY chart is generated for EVERY SENTENCE that we want to translate
# parsing starts by initializing the lexical rule applications that exist in our table
# there are no special rules -- any phrase can be combined, we're just looking for the top-scoring ones
# TODO: every derivation needs to contain 2 things: (1) its partial score, and (2) its English translation
# a derivatiton should be a dict with 2 keys: derivation, and score
# should we store the reordering decision?
# answer: not yet, only when it's needed, for now we assume monotone anyway

class CKY:
    def __init__(self, sentence_phrases, db_phrase_table):
        self.dbPT = db_phrase_table
        self.sen_length = len(sentence_phrases[0])
        self.parse_table = self.initialize_table(sentence_phrases)

    def initialize_table(self, sentence_phrases):
        parse_table = defaultdict(list)
        sen_length = self.sen_length
        for level_index, level in enumerate(sentence_phrases):
            for i, j, phrase in zip(range(1,len(level)+1), range(level_index+1, sen_length+1), level):
                p = " ".join(phrase)
                all_matches = self.dbPT.get_all_matches((p,))
                if all_matches is not None:
                    # initialize derivation objects for every match
                    derivations = [Derivation(match['target'], self.apply_lexical_rule(match)) for match in all_matches]
                    # remove zeros
                    derivations = filter(lambda d: d.score != 0 , derivations)

                    # sort derivations by lexical score
                    ordered_derivations = sorted(derivations, key=lambda d: d.score)[::-1]

                    #print "filled cell (%i,%i)" % (i,j)
                    parse_table[(i,j)] = ordered_derivations

        return parse_table

    # TODO: we need to learn weights for all of these features
    # TODO: this is actually a static method, not unique to each parser object
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
        # remove those stupid "-inf" tiny scores
        if lex_rule_score == float("-inf"):
            lex_rule_score = 0.0
        return lex_rule_score

    # TODO: add arguments to determine the type of parsing, i.e. monotone, simple reorder, etc...
    # TODO: add pruning methods (see args in method signature)
    # TODO: for testing, we need a way to see the source phrases at a cell -- what is the segmentation, and how is it being translated
    def decode(self, top_n=40, threshold=0.5):
        num_cols = self.sen_length
        for level in range(2, num_cols+1):
            for i,j in zip (range(1,num_cols+1), range(level, num_cols+1)):
                # get all of the derivations
                num_pairs = level-1
                for left_j,right_i in zip(range(1, j)[-num_pairs:], range(i+1, num_cols+1)):
                    # TODO: write a test for the cell pairs
                    #print "CELL PAIR:"
                    #print "Left cell: (%i,%i)" % (i,left_j)
                    #print "Right cell: (%i,%i)" % (right_i,j)

                    if self.parse_table[(i,left_j)] and self.parse_table[(right_i,j)]:
                        #print "BOTH CELLS CONTAIN DERIVATIONS"
                        left_phrases = [d.phrase for d in self.parse_table[(i,left_j)]]
                        left_derivations = self.parse_table[(i,left_j)]
                        right_phrases = [d.phrase for d in self.parse_table[(right_i,j)]]
                        right_derivations = self.parse_table[(right_i,j)]
                        # TODO: every new pair must become a new derivation object
                        # TODO: temporary hack to get some output
                        all_pairs = list(itertools.product(left_derivations, right_derivations)) + list(itertools.product(right_derivations, left_derivations))

                        all_phrases = [tokenizer.tokenize(str(l.phrase + " " + r.phrase)) for l,r in all_pairs]
                        #print "\n\n10 FROM ALL PHRASES"
                        #print all_phrases[1:10]
                        phrases_and_derivations = zip(all_phrases, all_pairs)
                        # add the exisiting two scores, and the language model score of the new phrase
                        # TODO: remember that the language model can currently return 0 when it doesn't know a token
                        new_scores = [(lm.get_lm_score(phrase) + pair[0].score + pair[1].score) for phrase, pair in phrases_and_derivations]
                        scores_and_phrases = zip(all_phrases, new_scores)
                        all_derivations = [Derivation(" ".join(p),s) for p,s in scores_and_phrases]
                        derivations_by_score = sorted(all_derivations, key=lambda d: d.score)[::-1][:20]
                        self.parse_table[(i,j)] += derivations_by_score[:top_n]

                        print "HERE ARE THE TOP 20 NEW DERIVATIONS FOR CELL %i,%i" % (i,j)
                        top_20 = derivations_by_score[:20]
                        for place,d in enumerate(top_20):
                            print "%i: %s" % (place,d.phrase)

                        # TODO: add these derivations to any existing derivations (from the lexical rule) in this cell

                    else:
                        print "one or both cells don't have a derivation"

        #we're finished now, so check the top 10 derivations in (1, num_cols)
        best_translations = sorted(self.parse_table[(1,num_cols)], key=lambda d: d.score)[::-1][:20]
        print "HERE ARE THE BEST FINAL TRANSLATIONS IN CELL (1,%i) " % num_cols
        for n,t in enumerate(best_translations):
            print "%i: %s\n\tSCORE: %f " % (n,t.phrase,t.score)


class Derivation:
    def __init__(self, phrase, score):
        self.phrase = phrase
        self.score = score
    def toString(self):
        return "{ \"phrase\": \"%s\", \"score\": %f }" % (self.phrase, self.score)

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
