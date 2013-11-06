#!/usr/bin/env python

# TODO: note for filling cells:
#   - at each level of the tree/chart, the number of phrases decreases by 1
# return all phrases from a sentence -- this implementation gets phrases size 2-len(phrase)
def all_phrases(phrase, max_len):
    phrase_list = []
    # TODO: each field contains multiple values which are objects of their own
    for i in range(1, max_len):
        phrase_list.append([phrase[j:j+i] for j in xrange(len(phrase)-i+1)])
    phrase_list.append([phrase])
    return phrase_list



