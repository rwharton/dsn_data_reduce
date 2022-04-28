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

The next bit specifies the RA and Dec strings:

    ################
    ##  RA / DEC  ##
    ################
    
    # RA and Dec strings needed for prepfil
    ra_str  = "050803.54"
    dec_str = "+260338.4"

these are needed for `prepfil`.

Next we set the time (in minutes) at the beginning of the obs 
to use for finding a bandpass with `prepfil`:

    ###########################
    ##  Bandpass Correction  ##
    ###########################
    
    # Time (minutes) to use for bpass solution
    bpass_tmin = 5.0

I have been using 5 minutes and that seems to work.

Next are params for various runs of `rfifind`:

    ###########################
    ##  rfifind RFI masking  ##
    ###########################
    
    # rfifind paramters.  A "1" indicates the rfifind step
    # done during bandpass.  A "2" indicates the rfifind
    # done after the averaging filter.
    
    rfi_time     = 0.0
    rfi_chanfrac = 0.1
    rfi_clip1    = 1.5  # before avg filter
    rfi_clip2    = 0.0  # after avg filter
    rfi_freqsig  = 16.0

The pipeline runs `rfifind` two times during processing and 
you may want things to be slightly different for each pass.  The 
first run of `rfifind` is when the bandpass is calculated.  We 
calculate and apply a preliminary bandpass, then run `rfifind`, 
then calculate and apply the next bandpass.  This mitigates any 
effects of very strong RFI on the bandpass.  The second run is 
after the running average filter.  Paramters with a 1 indicate 
the `rfifind` run during bandpass and the 1 indicates the run 
after the running average filter.

Next is the moving average filter:

    #############################
    ##  Moving Average Filter  ##
    #############################
    
    # Time const should be ~3 x Pspin
    avg_filter_timeconst = 10.0 # Pspin = 1.36
    avg_filter_nproc     = 30

This is the one parameter that will likely be the most 
dependent on your observing target.  The time constant 
should be at least 3 times the spin period of the pulsar 
you are looking at.  The other parameter sets the max number 
of processes to be spawned for the filtering.  


