maxent-decoder
==============

Working repo for an implementation of the Maxent-based reordering model + decoder described in Xiong et al 2006

This project implements the MaxEnt Decoder of Deyi Xiong et al    
[read it here](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.95.2554)

the parser is chart-based CKY

Calculating the Lexical Score
============================

For now, this project uses the Python wrapper for SRILM models from [pysrilm](https://github.com/njsmith/pysrilm). You'll need to install SRILM and pysrilm, and make sure that your SRILM language model is in the right place.
