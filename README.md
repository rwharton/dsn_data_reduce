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

Basic usage is as follows

    usage: dsn_reduce.py [-h] [-t TCONST] [-z ZAP] infile outdir outbase src
    
    Standard reduction of DSN data
    
    positional arguments:
      infile                Input file name
      outdir                Output data directory
      outbase               Base of output file (no extension)
      src                   Source Name (as in info file)
    
    optional arguments:
      -h, --help            show this help message and exit
      -t TCONST, --tconst TCONST
                            Filter time constant (def: 5.0)
      -z ZAP, --zap ZAP     Filter frequency - comma separated list giving the center frequency, the number of
                            harmonics beyond fundamental, and width in Hz (e.g., '60.0,5,1.0' to 60Hz signal
                            and 5 harmonics with width 1.0Hz. To zap multiple frequencies, repeat this argument

The source name is the "source id" in the "source_info.txt" file. 
This file contains the RA and Dec for sources that are typically 
observed.  If your source is not in there, just add it.  The 
source file should be in the same directory as the scripts.
