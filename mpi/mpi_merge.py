#!/usr/bin/env python
"""
Merge several HDF5 or ASCII files.

Merge all files that have a common (given) pattern in the name.
The patterns may be numbers and/or characters. Example: 'YYYYMMDD', 
where YYYY is year, MM is month and DD is day.

"""
# Fernando <fpaolo@ucsd.edu>
# November 2, 2012 

import os
import sys
import re
import numpy as np
import tables as tb
import argparse as ap
from mpi4py import MPI

# parse command line arguments
parser = ap.ArgumentParser()
parser.add_argument('files', nargs='+', help='HDF5 2D file[s] to merge')
parser.add_argument('-p', dest='pattern', default="_\d\d\d\d\d\d\d\d", 
    help="pattern to match in the file names, default '_\d\d\d\d\d\d\d\d'")
parser.add_argument('-o', dest='prefix', default='all_', 
    help='prefix of output file name, default all_')
parser.add_argument('-s', dest='suffix', default='', 
    help='suffix of output file name, default none')
parser.add_argument('-n', dest='count', action='store_const', const=True, \
    default=False, help='count number of tasks and exit, default no')
args = parser.parse_args()


def close_files():
    for fid in tb.file._open_files.values():
        fid.close() 

def get_files_to_merge(files, pattern):
    tomerge = {}
    patterns = np.unique(re.findall(pattern, ' '.join(files)))
    for s in patterns:
        tomerge[s] = [f for f in files if s in f]
    return tomerge

def get_fname_out(stem, fnamein, pref='', suf=''):
    path = os.path.split(fnamein)[0]
    return os.path.join(path, ''.join([pref, stem, suf, '.h5']))

def get_shape_out(files):
    nrows = 0
    for fname in files:
        f = tb.openFile(fname, 'r')
        data = f.getNode('/data')
        nrow, ncols = data.shape
        nrows += nrow
        f.close()
    return (nrows, ncols)

def merge_files(fname, shape, files):
    print 'merging:\n', files
    print 'into:\n', fname, '...'
    fout = tb.openFile(fname, 'w')
    nrows, ncols = shape
    atom = tb.Atom.from_type('float64')
    filters = tb.Filters(complib='zlib', complevel=9)
    dout = fout.createEArray('/', 'data', atom=atom, 
        shape=(0, ncols), filters=filters)
    for fnamein in files:
        fin = tb.openFile(fnamein, 'r')
        data = fin.getNode('/data')
        dout.append(data[:])
    close_files()
    print 'done.'

def merge_all(tomerge, pref='', suf=''):
    for patt, fnames in tomerge.items():
        fnameout = get_fname_out(patt, fnames[0], pref, suf)
        shape = get_shape_out(fnames)
        merge_files(fnameout, shape, fnames)

# MPI functions

def simple_partitioning(length, num_procs):
    sublengths = [length/num_procs]*num_procs
    for i in range(length % num_procs):    # treatment of remainder
        sublengths[i] += 1
    return sublengths

def get_subproblem_input_args(input_args, my_rank, num_procs):
    sub_ns = simple_partitioning(len(input_args), num_procs)
    my_offset = sum(sub_ns[:my_rank])
    my_input_args = input_args[my_offset:my_offset+sub_ns[my_rank]]
    return my_input_args

def program_to_run(string):
    if '.py' in string:
        run = 'python '
    else:
        run = '' # './'
    return run

#-------------

# If needed, uses `glob` to avoid Unix limitation on number of cmd args.
# To use it, instead of _file names_ pass a _str_ with "dir + file pattern".
if len(args.files) > 1:
    files = args.files
else:
    from glob import glob
    files = glob(args.files[0])   

pattern = str(args.pattern)
pref = args.prefix
suf = args.suffix
count = args.count
#path, _ = os.path.split(files[0])          # path of first file

print 'pattern to match:', pattern
print 'total files:', len(files)

comm = MPI.COMM_WORLD
my_rank = comm.Get_rank()
num_procs = comm.Get_size()

tomerge = get_files_to_merge(files, pattern)
if count: print 'number of tasks:', len(tomerge.items()); sys.exit()
my_tomerge = get_subproblem_input_args(tomerge.items(), my_rank, num_procs)
merge_all(dict(my_tomerge), pref=pref, suf=suf)

close_files()
