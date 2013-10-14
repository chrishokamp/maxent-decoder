#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import json

def makehash():
    return defaultdict(makehash)

def jsonString(obj):
    return json.dumps(obj)






