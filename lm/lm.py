#!/usr/bin/env python
# -*- coding: utf-8 -*-

from srilm import LM
import numpy as np

LM_LOCATION = '/home/chris/projects/maxent_decoder/lm/europarl.srilm.gz'
# TODO: add a check for "lower", so it's not as confusing
lm = LM(LM_LOCATION, lower=True)

def get_lm_score(token_list):
    # convert to natural log -- the SRILM wrapper returns base10
    logprob = lm.total_logprob_strings(token_list)/np.log10(np.e)
    return logprob
