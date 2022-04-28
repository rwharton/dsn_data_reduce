# dsn_data_reduce

This is a pipeline for doing the basic processing steps for 
DSN L, S, and X band data (K-band data require more steps and 
will be contained in a different pipeline).  The main pipeline 
script (`data_reduce_bb.py`) is basically just a wrapper that 
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

The main pipeline is run by just 

    python data_reduce_bb.py

with the parameters of the particular processing run specified 
in the paramter file `data_reduce_params_bb.py`.

Let's now go through the paramter file.  

    ##########################
    ##  Processing Scripts  ##
    ##########################
    
    # Directory containing all the scripts here
    #   Note:  might have a different name if running in Docker
    src_dir = '/src'
    par_file = '%s/data_reduce_params_bb.py' %src_dir
    copy_par = True

The first thing to set is the 

