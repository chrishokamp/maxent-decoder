#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk as nltk
from collections import Counter
import itertools

# TODO: this part is language-specific
sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def separate_sentences(text):
    return sentence_tokenizer.tokenize(text)
