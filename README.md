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

The first thing to set is the full path to the directory 
containing the scripts here.  You can also decide if you 
want the paramter file copied to the output directory 
(specified later).  This is useful to have a record of 
what parameters were set for a given processing run.

Next we define the input and output data:

    #########################
    ##  Input/Output Data  ##
    #########################
    
    # Directory where data files are
    #   Note:  might have a different name if running in Docker
    indir = '/output'
    
    # Input file name
    infile = 'slcp-200us.fil'
    
    # Base name for output data products
    outbase = 'slcp-22m045'
    
    # Directory where everything will go
    #   Note:  might have a different name if running in Docker
    outdir = '/output'

The `indir` is the path to the directory containing the input 
data file `infile`.  The `outbase` is the base name for the 
output files and intermediate products (which will have various 
things appended to it).  The `outdir` is the path to the 
output directory.  **NOTE: the output directory should already 
exist before running this pipeline.**

The next step deals with the working directory:

    ###################
    ##  Working Dir  ##
    ###################
    
    # Directory where we are doing work
    # (For now just leave as outdir)
    workdir = outdir

In principle, you may want to do the processing in a 
directory different from where the output files are sent.
We can add this later, but for now you need to just leave it 
the same as the output directory.



