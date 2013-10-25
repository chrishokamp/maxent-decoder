#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description="The location of the moses phrase table")
parser.add_argument('filename', type=str)
filename = parser.parse_args().filename

print "the filename you specified is: %s" % filename

lines = [line.strip() for line in open(filename, 'r').readlines()]

# pickle/shelve and save the table

