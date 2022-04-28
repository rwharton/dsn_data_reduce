######################################################################
##                        PARAMETER FILE                            ##
##                             for                                  ##
##                  data_reduce_params_bb.py                        ##
######################################################################

##########################
##  Processing Scripts  ##
##########################

# Directory containing all the scripts here
#   Note:  might have a different name if running in Docker  
src_dir = '/src'
par_file = '%s/data_reduce_params_bb.py' %src_dir
copy_par = True

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

###################
##  Working Dir  ##
###################

# Directory where we are doing work
# (For now just leave as outdir)
workdir = outdir


################
##  RA / DEC  ##
################

# RA and Dec strings needed for prepfil
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

# rfifind paramters.  A "1" indicates the rfifind step 
# done during bandpass.  A "2" indicates the rfifind 
# done after the averaging filter.

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


