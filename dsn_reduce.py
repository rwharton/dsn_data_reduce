"""
Created on Tue Sep 4 16:00:45 2018

@author: pearlman

data_reduce.py

Modified on 18 Jan 2022 by rsw
"""

import getopt, sys
import copy
import os
import time
import glob 
import shutil

from subprocess import call, check_call, check_output, Popen

import numpy as np

import filterbank

import h5py
from scipy import signal
from threading import Thread
from argparse import ArgumentParser

import dsn_reduce_params as par
import bandpass_threshold as bp_zap


def get_inbase(infile):
    """
    Strip off suffix to get basename for a file
    """
    inbase = infile.rsplit('.', 1)[0]
    return inbase


def filename_from_path(inpath):
    """
    split path to get filename
    """
    fname = inpath.split('/')[-1]
    return fname


def check_input_file(indir, infile):
    """
    make sure input file exists
    """
    inpath   = "%s/%s" %(indir, infile)

    if not os.path.exists(inpath):
        print("Data file not found:")
        print("  %s" %inpath)
        sys.exit(0)
    else: 
        print("Found file:")
        print("  %s" %inpath)

    return inpath


def parse_zap(zlist):
    """
    Parse the list of f0,nh,df strings given as input 
    into arrays of f0, nh, and df
    """
    f0 = []
    nh = []
    ww = []
    for zz in zlist:
        print(zz)
        f0_ii, nh_ii, ww_ii = zz.split(',')
        f0.append( float(f0_ii) )
        nh.append( int(nh_ii) )
        ww.append( float(ww_ii) )
    f0 = np.array(f0)
    nh = np.array(nh)
    ww = np.array(ww)

    return f0, nh, ww


def get_comma_strings(f0, nharm, width):
    """
    Turn lists into comma separated strings
    """
    f0_str = ""
    nh_str = ""
    ww_str = ""
    N = len(f0)
    for ii in range(N):
        f0_str += "%.3f," %(f0[ii])
        nh_str += "%d," %(nharm[ii])
        ww_str += "%.1f," %(width[ii])

    f0_str = f0_str[:-1]
    nh_str = nh_str[:-1]
    ww_str = ww_str[:-1]

    return f0_str, nh_str, ww_str


def filter_freqs(infile, f0, nharm, width, outfile=None):
    """
    Filter out RFI signals and harmonics
    """
    tstart = time.time()

    src_dir = par.src_dir
    nproc   = par.filter_nproc

    if outfile is None:
        inbase = get_inbase(infile)
        outfile = "%s_filter.corr" %(inbase)
    else: pass

    f0_str, nh_str, ww_str = get_comma_strings(f0, nharm, width)
    
    filter_cmd = "python " +\
                 "%s/m_fb_freq_filter_parallel_new.py " %src_dir +\
                 "--inputFilename %s " %infile +\
                 "--outputFilename %s " %outfile +\
                 "--f0 %s " %f0_str +\
                 "--nharm %s " %nh_str +\
                 "--width %s " %ww_str +\
                 "--numProcessors %d " %nproc +\
                 "--clean"
    
    print(filter_cmd)
    call(filter_cmd, shell=True)

    tstop = time.time()
    tdur = tstop - tstart 

    return outfile, tdur


def bandpass(infile, outdir, outbase, ra_str, dec_str):
    """
    Bandpass correct data

    Run rfifind on corrected data

    Bandpass correct again after rfi masking
    """
    tstart = time.time()

    # First we do a bandpass on input data
    bpass_time = par.bpass_tmin 
   
    infile_name = filename_from_path(infile) 
    inbase = get_inbase(infile_name)
    outbase = "%s/%s" %(outdir, inbase)
    bfile1 = "%s_bp.corr" %(outbase)

    bp1_cmd = "prepfil " +\
              "--bandpass=%.2f " %bpass_time +\
              "--ra=%s " %ra_str +\
              "--dec=%s " %dec_str +\
              "%s %s" %(infile, bfile1)
    print(bp1_cmd)
    call(bp1_cmd, shell=True) 

    # Next we run rfifind
    rfi_time     = par.rfi_time
    rfi_chanfrac = par.rfi_chanfrac 
    rfi_clip1    = par.rfi_clip1 
    rfi_freqsig  = par.rfi_freqsig 

    rfi_base = "%s_bp" %outbase 
    
    rfi_cmd = "rfifind " +\
              "-time %.2f " %rfi_time +\
              "-chanfrac %.2f " %rfi_chanfrac +\
              "-clip %.2f " %rfi_clip1 +\
              "-freqsig %.2f " %rfi_freqsig +\
              "-filterbank %s " %bfile1 +\
              "-o %s " %rfi_base
    print(rfi_cmd)
    call(rfi_cmd, shell=True)

    # Now we run bandpass again with the rfi mask 
    bfile2 = "%s_bp_rfi.corr" %(outbase)
    mask_file  = "%s_rfifind.mask" %rfi_base

    bp2_cmd = "prepfil " +\
              "--bandpass=%.2f " %bpass_time +\
              "--ra=%s " %ra_str +\
              "--dec=%s " %dec_str +\
              "--mask %s " %mask_file +\
              "%s %s" %(infile, bfile2)
    print(bp2_cmd)
    call(bp2_cmd, shell=True) 

    # If it worked, delete intermediatary file
    if os.path.exists(bfile2):
        os.remove(bfile1)
    else: pass

    tstop = time.time()
    tdur = tstop - tstart 
    
    return bfile2, tdur


def filter_avg(infile, tconst):
    """
    Run moving average filter, then rfifind, then apply mask to data
    """
    tstart = time.time()

    src_dir = par.src_dir

    # First we run the moving average filter
    avg_tconst = tconst
    avg_nproc  = par.avg_filter_nproc

    inbase = infile.rstrip(".corr")
    avg1_file = "%s_avg.corr" %inbase
    
    avg_cmd = "python " +\
              "%s/m_fb_filter_norm_jit.py " %src_dir +\
              "--inputFilename %s " %infile +\
              "--outputFilename %s " %avg1_file +\
              "--timeConstLong %.2f " %avg_tconst +\
              "--numProcessors %d " %avg_nproc +\
              "--clean "
    print(avg_cmd)
    call(avg_cmd, shell=True)
    
    # Next we run rfifind
    rfi_time     = par.rfi_time
    rfi_chanfrac = par.rfi_chanfrac 
    rfi_clip2    = par.rfi_clip2 
    rfi_freqsig  = par.rfi_freqsig 
    
    rfi_base = "%s_avg" %inbase

    rfi_cmd = "rfifind " +\
              "-time %.2f " %rfi_time +\
              "-chanfrac %.2f " %rfi_chanfrac +\
              "-clip %.2f " %rfi_clip2 +\
              "-freqsig %.2f " %rfi_freqsig +\
              "-filterbank %s " %avg1_file +\
              "-o %s " %rfi_base
    print(rfi_cmd)
    call(rfi_cmd, shell=True)

    # Now apply mask with prepfil
    rfi_mask = "%s_rfifind.mask" %rfi_base
    avg2_file = "%s_avg_masked.corr" %inbase

    prep_cmd = "prepfil " +\
               "--mask=%s " %rfi_mask +\
               "%s %s " %(avg1_file, avg2_file) 
    print(prep_cmd)
    call(prep_cmd, shell=True)

    # If successful, remove intermediary file
    if os.path.exists(avg2_file):
        os.remove(avg1_file)
    else: pass

    tstop = time.time()
    tdur = tstop - tstart 
    
    return avg2_file, tdur


def rename_output_file(infile, outdir, outbase):
    """
    Link infile to clear output name
    """
    outfile = "%s/%s_final.fil" %(outdir, outbase)

    # Check that target file doesnt already exist
    if os.path.isfile(outfile):
        print("File exists:  %s" %outfile)
        print("Skipping final link...")
        return 
    else: pass

    mv_cmd = "mv %s %s" %(infile, outfile)
    print(mv_cmd)
    call(mv_cmd, shell=True)
    
    return


def delete_files(flist):
    """
    Delete files in list flist
    """
    for dfile in flist:
        if os.path.exists(dfile):
            os.remove(dfile)
        else:
            continue
    return


def organize_output(outdir):
    """
    organize output files into folders

    NOTE: We are assuming everything already in output dir
    """
    top_dir = outdir 

    # Place for rfifind masks
    mask_dir = "%s/masks" %(top_dir)
    os.mkdir(mask_dir)
    
    # Place for bandpass files
    bpass_dir = "%s/bpass" %(top_dir)
    os.mkdir(bpass_dir)

    # Get rfifind files and move to mask
    rfi_files = glob.glob("%s/*rfifind*"%(top_dir))
    for rfi_file in rfi_files:
        shutil.move(rfi_file, mask_dir)

    # Get *.bpass files and move to bpass
    bpass_files = glob.glob('%s/*.bpass' %(top_dir))
    for bpass_file in bpass_files:
        shutil.move(bpass_file, bpass_dir)
    
    # Get *.bandpass files and move to bpass
    bpass2_files = glob.glob('%s/*.bandpass' %(top_dir))
    for bpass2_file in bpass2_files:
        shutil.move(bpass2_file, bpass_dir)

    # Move plots to bpass
    bpng_files = glob.glob('%s/*bp_zap.png' %(top_dir))
    for bpng_file in bpng_files:
        shutil.move(bpng_file, bpass_dir)

    return


#######################
##  Get Source Info  ##
#######################

def radec_fmt(cstr):
    """
    Convert hh:mm:ss / dd:mm:ss to SIGPROC
    header format of hhmmss or ddmmss
    """
    ostr = ''.join( cstr.split(':') )
    return ostr


def get_info(name):
    """
    Get info for source id "name"
    """
    info_file = par.info_file

    src_name = name
    ra  = "000000.0"
    dec = "+000000.0"
    obs_type = 'FRB'

    found = 0
    with open(info_file, 'r') as fin:
        for line in fin:
            if line[0] in ["\n", "#"]:
                continue
            cols = line.split()
            if len(cols) != 5:
                continue
            if cols[0] == name:
                src_name = cols[1]
                ra = radec_fmt(cols[2])
                dec = radec_fmt(cols[3])
                obs_type = cols[4]
                found = 1
                break
            else: pass

    if found == 0:
        print("")
        print("WARNING!  Source %s not found in info file!" %(name))
        print("")

    return src_name, ra, dec, obs_type



def parse_input():
    """
    Use argparse to parse input
    """
    prog_desc = "Standard reduction of DSN data"
    parser = ArgumentParser(description=prog_desc)

    #parser.add_argument('indir', help='Input data directory')
    parser.add_argument('infile', help='Input file name')
    parser.add_argument('outdir', help='Output data directory')
    parser.add_argument('outbase', help='Base of output file (no extension)')
    parser.add_argument('src', help='Source Name (as in info file)')
    parser.add_argument('-t', '--tconst',
                        help='Filter time constant (def: 5.0)',
                        required=False, type=float, default=5.0)
    parser.add_argument('-z', '--zap', 
           help='Filter frequency - comma separated list giving the '+\
                'center frequency, the number of harmonics beyond ' +\
                'fundamental, and width in Hz (e.g., \'60.0,5,1.0\' to '+\
                '60Hz signal and 5 harmonics with width 1.0Hz.  To zap '+\
                'multiple frequencies, repeat this argument',
           action='append', required=False, default=[])

    args = parser.parse_args()

    #indir = args.indir
    outdir = args.outdir
    infile = args.infile
    outbase = args.outbase
    src = args.src
    tconst = args.tconst
    zaplist = args.zap

    #return indir, outdir, infile, outbase, src
    return outdir, infile, outbase, src, tconst, zaplist



def main():
    """
    Call all of the processing steps
    
    Info will come from param file
    
    Time the non trivial steps
    """
    tstart = time.time()

    # Parse input
    outdir, infile, outbase, src, tconst, zaplist = parse_input()

    # Get source info from source_info.txt
    src_name, ra_str, dec_str, obs_type = get_info(src)

    # Print pars
    print("infile: %s" %infile)
    print("outdir: %s" %outdir)
    print("outbase: %s" %outbase)
    print("")
    print("Source: %s" %src)
    print("ra:   %s" %ra_str)
    print("dec: %s" %dec_str)
    print("tconst: %.2f" %tconst)
    print("zap: %s" %( "; ".join(zaplist)))
    print("") 
    #print(zaplist)

    # Get file paths based on param file
    #infile = check_input_file(indir, infile)
    
    #sys.exit()

    # Copy par file to out dir
    if par.copy_par:
        shutil.copy(par.par_file, outdir)

    # Filter out RFI frequencies if specified
    if len(zaplist):
        print(zaplist)
        f0_arr, nharm_arr, width_arr = parse_zap(zaplist)
        filter_file, filter_time = filter_freqs(infile, f0_arr,
                                                nharm_arr, width_arr)
    else:
        filter_file = infile
        filter_time = 0.0

    # Bandpass + RFI + Bandpass
    #bpass_file, bpass_time = bandpass(infile, outdir, outbase, ra_str, dec_str)
    bpass_file, bpass_time = bandpass(filter_file, outdir, outbase, 
                                      ra_str, dec_str)

    # Running avg baseline filter
    bpass_bl_file, avg_time = filter_avg(bpass_file, tconst)
    
    # Rename final cal file to cleaner output name
    rename_output_file(bpass_bl_file, outdir, outbase)

    # Organize output
    organize_output(outdir)

    tstop = time.time()
    total_time = tstop - tstart

    # Now print summary of times
    print("##################################################")
    print("##              TIME SUMMARY                    ##")
    print("##################################################")
    print("")    
    print("Filter:             %.1f minutes" %(filter_time/60.))
    print("Bandpass:           %.1f minutes" %(bpass_time/60.))
    print("Baseline:           %.1f minutes" %(avg_time/60.))
    print("") 
    print("Total Time:         %.1f minutes" %(total_time/60.))
     
    return

debug = 0
    
if __name__ == "__main__":
    if debug:
        pass
    else:
        main()
