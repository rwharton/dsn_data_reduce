# dsn_data_reduce

This is a pipeline for doing the basic processing steps for 
DSN L, S, and X band data (K-band data require more steps and 
will be contained in a different pipeline).  The main pipeline 
script (`dsn_reduce.py`) is basically just a wrapper that 
will call various other tasks (e.g., `prepfil`) and scripts 
mostly written by Aaron Pearlman.  

This pipleine is only applicable for DSN data and uses software 
that has often been hard coded for DSN compatability.  

## Dependencies 

In addition to the scripts included in here you will need to 
have installed `prepfil` and `PRESTO`.  I think you will need 
the most recent version of `PRESTO` because the behavior of 
the `filterbank` python module has changed slightly, but I 
have not tested it.

## Instructions 

usage: dsn_reduce.py [-h] infile outdir outbase src

Standard reduction of DSN data

positional arguments:
  infile      Input file name
  outdir      Output data directory
  outbase     Base of output file (no extension)
  src         Source Name (as in info file)

optional arguments:
  -h, --help  show this help message and exit
