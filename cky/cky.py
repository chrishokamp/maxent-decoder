#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from collections import Counter
from collections import defaultdict
import itertools
import numpy as np
import phrase_table.DB_Phrase_Table
import lm.lm as lm
import preprocess.tokenizer as tokenizer

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
                        # TODO: temporary hack to get some output -- pruned at 100 for efficiency
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

                        # TODO: merge phrases which begin and end in the same token

                        # NOTE: includes 20 cutoff hack for efficiency
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

