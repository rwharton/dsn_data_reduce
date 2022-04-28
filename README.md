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

## Output 

## Running in Docker

Because we have a bit of a delicate dependency ecosystem here, 
it can be useful to use a docker image with everything on it.  
Here we'll give a very short example for how to do that.

First, you want to make sure you have the docker image on your 
machine.  You can see what images are there by running:

    docker images

which will give output like this:

    REPOSITORY     TAG       IMAGE ID       CREATED        SIZE
    dsn_soft       latest    5a68f31b291c   2 months ago   7.6GB
    dsn_pearlman   latest    5a68f31b291c   2 months ago   7.6GB
    ubuntu         focal     54c9d81cbb44   2 months ago   72.8MB

for this, we want to use `dsn_soft`.

Before we run anything, we want to make sure we know our data 
directory, output directory, and source directory.  For this test 
example I will use a 2-min snippet of R67 data.

The filterbank file `srcp-0001.fil` is in:

    /export/data1/wharton/example/fil

and I want the results of the processing to go in 

    /export/data1/wharton/example/proc

I have the source files for running the pipeline in:

    /home/wharton/software/scripts/pipeline

When we run docker, we will need to specify the volumes we want 
to have access to, so we will need to include these.  We will also 
be able to give them simpler names.

Now we are going to make the docker command to create our docker 
environment.  If your processing is expected to take a long time 
and you are just using a terminal, you might want to start a screen 
session now.

To start our docker environment we run the following command:

    docker run -e DISPLAY -v $HOME/.Xauthority:/home/psr/.Xauthority --net=host --rm -ti -v /export/data1/wharton/example/fil:/data -v /export/data1/wharton/example/proc:/output -v /home/wharton/software/scripts/pipeline:/src dsn_soft bash

There's a lot going on there, so let's break it down.  A simplified version 
of this would just be:

    docker run --rm -ti dsn_soft bash

which means to run the docker image `dsn_soft` in interactive mode `-ti` and 
kill the environment when we are done `--rm`.  Within the environment run 
the command `bash`.   So basically this just gives us a terminal within the 
docker virtual environment.  You can try just running this if you want.  If 
you do you will see a directory called `software` where we have installed 
all the software we need.  But the larger filesystem is not accessible.  

We mount other directories using the `-v` option.  For example:

    -v /export/data1/wharton/example/fil:/data

This takes the directory `/export/data1/wharton/example/fil` and mounts 
it as `/data` in the docker environment.  You can just try that out if 
you want:

    docker run --rm -ti -v /export/data1/wharton/example/fil:/data dsn_soft bash

If you run that you will now see a `/data`:

    root@8d8e31ecc2f6 [28 Apr 2022 22:05] ~> ls /data
    srcp-0001.fil

If you create a file here in the docker environment it will show up in the 
real filesystem as well.  Same if you remove something.  You should be a little 
careful about this because in the docker environment you have root permissions. 
If you kill something in the docker environment, it will die in real life too.

OK, the last part of the long command was this stuff:

    -e DISPLAY -v $HOME/.Xauthority:/home/psr/.Xauthority --net=host

This is needed to make x11 forwarding work, which you might want.

OK, let's now set up our parameter file, taking in mind the names of 
our directories will change in docker based on what we have called them 
in the docker command.  

We'll now make the following edits in the `data_reduce_params_bb.py` file:

    ##########################
    ##  Processing Scripts  ##
    ##########################
    src_dir = '/src'
    
    #########################
    ##  Input/Output Data  ##
    #########################
    indir = '/data'
    infile = 'srcp-0001.fil'
    outbase = 'test'
    outdir = '/output'
    
    ################
    ##  RA / DEC  ##
    ################
    ra_str  = "050803.54"
    dec_str = "+260338.4"

OK, so now we are ready to go.  

Let's run the docker command above:

    docker run -e DISPLAY -v $HOME/.Xauthority:/home/psr/.Xauthority --net=host --rm -ti -v /export/data1/wharton/example/fil:/data -v /export/data1/wharton/example/proc:/output -v /home/wharton/software/scripts/pipeline:/src dsn_soft bash

which will take you into the docker environment.  You can double check that 
the data and src directories point where you think:

    root@tefim2 [28 Apr 2022 22:26] ~> ls /data
    srcp-0001.fil
    
    root@tefim2 [28 Apr 2022 22:26] ~> ls /src
    README.md              data_reduce_bb.py         fb_utils.py
    m_fb_freq_filter_parallel_new.py
    bandpass_threshold.py  data_reduce_params_bb.py  m_fb_filter_norm_jit.py  
    m_fb_zapchan.py

and things look correct.

So now we just run the pipeline script:

    root@tefim2 [28 Apr 2022 22:29] ~> python /src/data_reduce_bb.py

and you should get some information about the ongoing processing.





