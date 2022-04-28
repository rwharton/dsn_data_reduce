#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 15:14:37 2018

@author: pearlman

Aaron B. Pearlman
aaron.b.pearlman@caltech.edu
Division of Physics, Mathematics, and Astronomy
California Institute of Technology
Jet Propoulsion Laboratory

m_fb_60hzfilter_parallel.py - Script for filtering out 60 Hz instrumental noise
                              (and harmonics at 120 Hz and 180 Hz) from each
                              channel of the filterbank file, with parallelization
                              capabilities.

"""

import getopt, sys
from subprocess import call, check_call, check_output, Popen

import numpy as np
import matplotlib.pyplot as plt
import sys
import copy
import h5py

sys.path.append("/Users/aaron/pulsar_software/presto/lib/python/")
import filterbank

from scipy import signal

from threading import Thread


BLOCKSIZE = 1e6

def readFilterbank(inputFilename, logFile=""):
    """
    Read the filterbank file into memory. Store the data in a
    dynamically accessible h5py file, stored in a binary .hdf5 file.
    """
    if (logFile == ""):
        print("Reading filterbank file (%s)...\n" % inputFilename)
    else:
        logFile.write("Reading filterbank file (%s)...\n\n" % inputFilename)

    fb = filterbank.FilterbankFile(inputFilename)

    inputHeader = copy.deepcopy(fb.header)
    inputNbits = fb.nbits
    totalChans = fb.nchans
    nchans = np.arange(0, fb.nchans-1, 1) # Top of the band is index 0.
    freqs = fb.frequencies
    startbin = 0
    endbin = fb.nspec
    nspec = np.subtract(endbin, startbin)
    nblocks = int(np.divide(nspec, BLOCKSIZE))
    remainder = nspec % BLOCKSIZE
    totalBlocks = nblocks

    if (remainder):
        totalBlocks = nblocks + 1

    h5pyFile = h5py.File("%s.hdf5" % inputFilename, "w")
    spectraData = h5pyFile.create_dataset("data", (totalChans, nspec), dtype="float32")

    for iblock in np.arange(0, nblocks, 1):
        print(iblock)
        progress = np.multiply(np.divide(iblock + 1.0, totalBlocks), 100.0)
        if (logFile == ""):
            sys.stdout.write("Reading... [%3.2f%%]\r" % progress)
            sys.stdout.flush()
        else:
            logFile.write("Reading... [%3.2f%%]\n" % progress)

        lobin = int(np.add(np.multiply(iblock, BLOCKSIZE), startbin))
        hibin = int(np.add(lobin, BLOCKSIZE))
        read_nspec = hibin-lobin
        spectra = fb.get_spectra(lobin, read_nspec)
        
        spectraData[:, lobin:hibin] = spectra[:, :]

        #for ichan in np.arange(0, totalChans, 1):
        #    print(ichan)
        #    spectraData[ichan, lobin:hibin] = spectra[ichan, :]

    if (remainder):
        progress = np.multiply(np.divide(iblock + 2.0, totalBlocks), 100.0)

        if (logFile == ""):
            sys.stdout.write("Reading... [%3.2f%%]\r" % progress)
            sys.stdout.flush()
        else:
            logFile.write("Reading... [%3.2f%%]\n" % progress)

        lobin = int(np.subtract(endbin, remainder))
        hibin = int(endbin)
        read_nspec = hibin-lobin
        spectra = fb.get_spectra(lobin, read_nspec)

        spectraData[:, lobin:hibin] = spectra[:, :]
        #for ichan in np.arange(0, totalChans, 1):
        #    spectraData[ichan, lobin:hibin] = spectra[ichan, :]

    if (logFile == ""):
        print("\n")
    else:
        logFile.write("\n")

    return spectraData, inputHeader, inputNbits, h5pyFile;


def writeFilterbank(outputFilename, spectraData, inputHeader, inputNbits, logFile=""):
    """
    Write the filterbank data from memory to a filterbank file.
    """
    if (logFile == ""):
        print("Writing filterbank file (%s)...\n" % outputFilename)
    else:
        logFile.write("Writing filterbank file (%s)...\n\n" % outputFilename)

    filterbank.create_filterbank_file(outputFilename, inputHeader, nbits=inputNbits)
    outfil = filterbank.FilterbankFile(outputFilename, mode='write')

    startbin = 0
    endbin = np.shape(spectraData)[1]

    nblocks = int(np.divide(endbin, BLOCKSIZE))
    remainder = endbin % BLOCKSIZE
    totalBlocks = nblocks

    if (remainder):
        totalBlocks = nblocks + 1

    for iblock in np.arange(0, nblocks, 1):
        progress = np.multiply(np.divide(iblock + 1.0, totalBlocks), 100.0)
        if (logFile == ""):
            sys.stdout.write("Writing... [%3.2f%%]\r" % progress)
            sys.stdout.flush()
        else:
            logFile.write("Writing... [%3.2f%%]\n" % progress)

        lobin = int(np.add(np.multiply(iblock, BLOCKSIZE), startbin))
        hibin = int(np.add(lobin, BLOCKSIZE))

        spectra = spectraData[:,lobin:hibin].T
        outfil.append_spectra(spectra)

    if (remainder):
        progress = np.multiply(np.divide(iblock + 2.0, totalBlocks), 100.0)
        if (logFile == ""):
            sys.stdout.write("Writing... [%3.2f%%]\r" % progress)
            sys.stdout.flush()
        else:
            logFile.write("Writing... [%3.2f%%]\n" % progress)

        lobin = int(np.subtract(endbin, remainder))
        hibin = int(endbin)

        spectra = spectraData[:,lobin:hibin].T
        outfil.append_spectra(spectra)

    if (logFile == ""):
        print("\n")
    else:
        logFile.write("\n")

    return;


def butter_bandstop(nyq, cutoff_freq_start, cutoff_freq_stop, order=3):
    """ 
    Create a butterworth bandstop filter 
    (use a digital filter for real data!). 
    """
    cutoff_freq_start = cutoff_freq_start / nyq
    cutoff_freq_stop = cutoff_freq_stop / nyq
    
    b, a = signal.butter(order, [cutoff_freq_start, cutoff_freq_stop], btype="bandstop", analog=False)
    
    return b, a


def fb_filter_60Hz(fb_data, fb_header, numProcessors, logFile=""):
    """ 
    Filter 60 Hz signal and higher order harmonics (120 Hz, 180 Hz) 
    from the fb file.
    Typical attenuation is ~120-150 dB around the filtered frequencies. 
    """
    timeRes = float(fb_header["tsamp"])
    nsamples = np.shape(fb_data)[1]
    duration = np.divide(np.multiply(nsamples, timeRes), 3600.0)
    
    print("Time Resolution: %.6f s" % timeRes)
    print("nsamples: %i" % nsamples)
    print("Duration: %.2f hr\n" % duration)
    
    nchans = float(fb_header["nchans"])
    
    fs = 1.0 / timeRes
    nyq = 0.5 * fs
    
    cutoff_freq_center_17a064 = [60.0, 119.989, 179.979] # K-band, 17a064
    cutoff_freq_center = [60.015, 120.015, 180.015] # K-band, 16a240
    cutoff_freq_width = 1.0
    cutoff_freq_start = np.subtract(cutoff_freq_center, cutoff_freq_width)
    cutoff_freq_stop = np.add(cutoff_freq_center, cutoff_freq_width)
    
    # Apply the butterworth filter to one channel of the filterbank file.
    def worker(ichan):
        fb_data[ichan] = signal.filtfilt(b, a, fb_data[ichan])
    
    for iFilter in np.arange(0, len(cutoff_freq_center), 1):
        print("Filtering frequency: %.1f Hz" % cutoff_freq_center[iFilter])
        b, a = butter_bandstop(nyq, cutoff_freq_start[iFilter], cutoff_freq_stop[iFilter], order=3)
        w, h = signal.freqz(b, a, worN=100000)
        
        # Need to parallelize filtering channel by channel.
        ichan = 0
        for iBatch in np.arange(0, int(nchans / numProcessors), 1):
            threads = []
            for iProcess in np.arange(0, numProcessors, 1):
                ichan = int(iProcess + (iBatch * numProcessors))
                
                t = Thread(target=worker, args=(ichan,))
                threads.append(t)
                
                progress = np.multiply(np.divide(ichan + 1.0, nchans), 100.0)
                
                if (logFile == ""):
                    print("Filtering [%.1f Hz]: Channel %i [%3.2f%%]" %(\
                          cutoff_freq_center[iFilter], nchans - ichan, progress))
                else:
                    logFile.write("Filtering [%.1f Hz]: Channel %i [%3.2f%%]\n" %(\
                          cutoff_freq_center[iFilter], nchans - ichan, progress))
            
            for x in threads:
                x.start()
            
            for x in threads:
                x.join()
        
        if (nchans % numProcessors):
            threads = []
            for ichan2 in np.arange(ichan + 1, int(nchans), 1):
                t = Thread(target=worker, args=(ichan2,))
                threads.append(t)
                
                progress = np.multiply(np.divide(ichan2 + 1.0, nchans), 100.0)
                
                if (logFile == ""):
                    print("Filtering [%.1f Hz]: Channel %i [%3.2f%%]" % (cutoff_freq_center[iFilter], nchans - ichan2, progress))
                else:
                    logFile.write("Filtering [%.1f Hz]: Channel %i [%3.2f%%]\n" % (cutoff_freq_center[iFilter], nchans - ichan2, progress))
            
            for x in threads:
                x.start()
            
            for x in threads:
                x.join()
        
        if (logFile == ""):
            print("\n")
        else:
            logFile.write("\n")
        
    return fb_data;



def usage():
    print("##################################")
    print("Aaron B. Pearlman")
    print("aaron.b.pearlman@caltech.edu")
    print("Division of Physics, Mathematics, and Astronomy")
    print("California Institute of Technology")
    print("Jet Propulsion Laboratory")
    print("##################################\n")

    print("""
    usage:  m_fb_60hzfilter_parallel.py [options]
        [-h, --help]                    : Display this help
        [--inputFilename]               : Name of input filterbank file
        [--outputFilename]              : Name of output filterbank file created after
                                          filtering is completed
        [--numProcessors]               : Number of processors to be used for parallelizing
                                          the filtering algorithm. Default is 1. Must be
                                          less than the total number of channels.
        [--outputDir]                   : Output directory where the products of the data
                                          analysis will be stored.
        [--logFile]                     : Name of the log file to store the data reduction
                                          output.
        [--clean]                       : Flag to clean up intermediate reduction products.
                                          Default is FALSE
        
        
        This program reads a filterbank file, stores it in dynamic memory,
        and then removes 60 Hz instrumental noise from each channel of the
        filterbank file. Harmonics of this signal (at 120 Hz and 180 Hz are
        also filtered). The filtered data is written to a new filterbank file.
        
    Example: m_fb_60hzfilter_parallel.py --inputFilename input.corr --outputFilename output.corr --numProcessors 100 --outputDir /home/pearlman/fb_data/ --clean

    """)



def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "inputFilename:outputFilename:timeConstLong:timeConstShort:numProcessors:outputDir:logFile:clean:",
                                   ["help", "inputFilename=", "outputFilename=",
                                    "numProcessors=", "outputDir=", "logFile=",
                                    "clean"])
    
    except getopt.GetoptError:
        # Print help information and exit.
        usage()
        sys.exit(2)
    
    if (len(sys.argv) == 1):
        usage()
        sys.exit(2)
    
    inputFilename=None
    outputFilename=None
    numProcessors=None
    outputDir=None
    logFile=None
    clean=None
    
    for o, a in opts:
        if (o in ("-h", "--help")):
            usage()
            sys.exit()
        
        if o in ("--inputFilename"):
            inputFilename = a
        if o in ("--outputFilename"):
            outputFilename = a
        if o in ("--numProcessors"):
            numProcessors = a
        if o in ("--outputDir"):
            outputDir = a
        if o in ("--logFile"):
            logFile = a
        if o in ("--clean"):
            clean = True
    
    if ((inputFilename == None) | (outputFilename == None)):
        usage()
        sys.exit()
    
    if (numProcessors != None):
        numProcessors = float(numProcessors)
        
    
    
    if ((outputDir != None) & (logFile != None)):
        writeFile = open("%s/%s" % (outputDir, logFile), "w")
        fb_data, fb_header, fb_Nbits, h5pyFile = readFilterbank(inputFilename, logFile=writeFile)
        
        if (numProcessors == None):
            numProcessors = 1
        
        fb_data = fb_filter_60Hz(fb_data, fb_header, numProcessors, logFile=writeFile)
        outputPath = "%s/%s" % (outputDir, outputFilename)
        
        if (outputDir == None):
             outputPath = outputFilename
        
        writeFilterbank(outputPath, fb_data, fb_header, fb_Nbits, logFile=writeFile)
        writeFile.close()
    
    else:
        fb_data, fb_header, fb_Nbits, h5pyFile = readFilterbank(inputFilename)
        
        if (numProcessors == None):
            numProcessors = 1
        
        fb_data = fb_filter_60Hz(fb_data, fb_header, numProcessors)
        outputPath = "%s/%s" % (outputDir, outputFilename)
        
        if (outputDir == None):
             outputPath = outputFilename
        
        writeFilterbank(outputPath, fb_data, fb_header, fb_Nbits)
    
    h5pyFile.close()
    
    if (clean == True):
        if (outputDir != None):
            call("rm -rf %s/*hdf5" % outputDir, shell=True)
        else:
            call("rm -rf *hdf5", shell=True)
    
    
if __name__ == "__main__":
    main()
