 ####################################
 # Avida Analysis Toolkit - v 0.1   #
 # A. W. Covert III, Ph. D          #
 # All rights reserved              #
 ####################################

#need os.walk and re.search
import os, re

from numpy import *

import gzip

### find all replicate avida runs
### return the full path of the specified output file
### in an avida data directory
  ###treat_prefix: a string continaing the prefix of a directory contianing a single avida replicate
  ###dat_file    : a string continaing the name of a particular dat file (including the extension)
def find_replicates(treat_prefix, dat_file, p="."):
    # container for filenames
    files = []

    # combined search string
    # assumes that seed # is not specified
    searchStr = treat_prefix+".*[-_][0-9]*/data"

    #debugging output
    #print "Searching directory {0:s}".format(os.path.abspath(p))

    # walk through the directories and find the replicates
    for path, names, filename in os.walk(p,False):
        
        sPath = re.search(searchStr, path)
        #debugging output
        #print "Examining {0:s}".format(path)

        # if we find the replicate...
        if(sPath != None):
            #print "Found " + path
            # and if we find the file
            for file in filename:
                if(re.search(dat_file,str(file)) != None):

                    #append the full filename back to the list
                    files.append(path+"/"+file)
    return files

### included for legacy purposes
def get_dominant_fitness(treatPrefix):
    
    return array(find_replicates(treatPrefix, "dominant\.dat\.gz"))


### dump the data out as a flat file easily readable by matlab
### inputs, data (list of lists), fp (output filepointer)
def dump_flat_file(data, fp):

    #debugging output
    #print data
    
    #for now we assume that num of rows is always the same
    #this is a reasonable assumption for a single treatment
    cols = len(data)
    rows = len(data[0])

    print "Printing {0:d} columns and {1:d} rows".format(cols, rows)

    # actually dump the file, cols will be treatments, rows will be timepoints
    for j in range(0,rows):
        line = ""
        for i in range(0,cols):
            line = "{0:s}{1: >24.8f}".format(line, data[i][j])

        line += "\n"

        fp.write(line)
    fp.close()



### return a given column from a standard avida file
### asssuming floating point data
def get_column(file,col):

    #list of stuff to return
    stuff = []



    #open a file
    fp = None
    if(file[-2:] == "gz"):
        fp = gzip.open(file)
    else:
        fp = open(file)

    #dump the entire file into 'data'
    data = fp.readlines()

    #close the filepointers
    fp.close()

    #each line contains a treatement
    for line in data:

        #make sure the line starts with a column
        if(re.search("^[0-9]+", line) != None):
            stuff.append(float(re.split(" ",line)[col-1]))

    return stuff

### return a given row from a standard avida file
### asssuming floating point data
def get_row(file, row):

    #list of stuff to return
    stuff = []

    fp = None

    if file[-2:] == "gz":
        #open a gzipped file
        fp = gzip.open(file)
    else:
        fp = open(file)

    #dump the entire file into 'data'
    data = fp.readlines()

    #close the filepointers
    fp.close()

    #each line contains a treatement
    for ln in range(0,len(data)):
        raw = []
        if ln == row:
            #print data[ln]
            raw = re.findall("\-?[0-9]+\.?[0-9]*",data[ln])
            #print raw
            for num in raw:
                if num != '':
                    stuff.append(float(num))

            #print stuff

            return stuff


### Grab all floating point data from a flat file
### Designed to be used with a file dumped from dump_flat_file() above
def get_matrix(file):
    #list of stuff to return
    stuff = []

    #open a gzipped file
    fp = open(file)

    #dump the entire file into 'data'
    data = fp.readlines()

    #close the filepointers
    fp.close()

    #each line contains a treatement
    for ln in range(0,len(data)):
        raw = []
        raw = re.findall("\-?[0-9]+\.?[0-9]*",data[ln])
        #print raw
        line = []
        for num in raw:
            if num != '':
                line.append(float(num))
        stuff.append(line)

    #Convert to a matrix with cols == treatments, row==time points
    return transpose(matrix(stuff))
    
