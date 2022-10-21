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
src_dir = '/src/reduce'
par_file = '%s/data_reduce_params_bb.py' %src_dir
info_file = '%s/source_info.txt' %src_dir
copy_par = True

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

avg_filter_nproc     = 30


