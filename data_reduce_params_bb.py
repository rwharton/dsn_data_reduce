######################################################################
##                        PARAMETER FILE                            ##
##                             for                                  ##
##                  data_reduce_params_bb.py                        ##
######################################################################

##########################
##  Processing Scripts  ##
##########################

src_dir = '/src'
par_file = '%s/data_reduce_params_bb.py' %src_dir
copy_par = True

#########################
##  Input/Output Data  ##
#########################

# Directory where data files are
#   Note:  might have a different name if running in Docker  
indir = '/output'

infile = 'slcp-200us.fil'
outbase = 'slcp-22m045'
outdir = '/output'

###################
##  Working Dir  ##
###################

# Directory where we are doing work
workdir = '/output' 


#################
##  Zap Chans  ##
#################

# Note that this will calc bpass with FULL data set
# May need / want to change this later

# Pars for filtering.  Diff thresh is the max fractional 
# deviation from running median.  Val thresh is min val. 
# nchan_win is window size for running stats
diff_thresh = 0.10
val_thresh  = 0.10 
nchan_win   = 32


################
##  RA / DEC  ##
################

# Not sure if we really need this 
ra_str  = "050803.54"
dec_str = "+260338.4"


###########################
##  Bandpass Correction  ##
###########################

# Time (minutes) to use for bpass solution
bpass_tmin = 5.0


###########################
##  rfifind RFI masking  ##
###########################

rfi_time     = 0.0 
rfi_chanfrac = 0.1 
rfi_clip1    = 1.5  # before avg filter 
rfi_clip2    = 0.0  # after avg filter
rfi_freqsig  = 16.0 


#############################
##  Moving Average Filter  ##
#############################

# Time const should be ~3 x Pspin
avg_filter_timeconst = 10.0 # Pspin = 1.36
avg_filter_nproc     = 30


###################################
##  Clean Up Intermediate Files  ##
###################################

# If true, delete intermediate *.corr files
cleanup = True


