#!/usr/bin/env python3
'''preprocess.py lib_id decl_out'''

import os, re, sys
import gzip, sqlite3
import argparse

miq =  30            # minimum quality value in fastq input
fel =  0             # max errors allowed in critical seq positions
db_rel = '../data'   # location of sqlite db file relative to script
db_fil = 'decl.db'
fq_dir = './'
par = dict()         # will hold library-specific parameters
spks = [(x,x,x) for x in range(1,10)]


# could/should make more of the above into options
parser = argparse.ArgumentParser()
parser.add_argument("libid", type=int, help="DECL library type (integer)")
parser.add_argument("decl", help="Extracted DECL data (out file)")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()
verbose = args.verbose


ex_dir = os.path.dirname(os.path.abspath(__file__))
db_loc = os.path.join(ex_dir, db_rel, db_fil)
dbf = os.path.realpath(db_loc)
if verbose: print(f"{dbf = }")

if not os.path.isfile(dbf) or not os.access(dbf, os.R_OK):
    print("Database not found at %s" % dbf)
    exit(0)
# else:
#     print(f"Using db at {dbf}")

# should wrap with catch, etc
dbh = sqlite3.connect(dbf)
sth = dbh.cursor()

def main():
    # check for overflow of qual sum?
    res = dict()
    libid, sample = args.libid, args.decl
    
    get_params(libid)

    f = fq_dir + sample
    if not os.path.isfile(f) or not os.access(f, os.R_OK):
        f += '.gz'
        if not os.path.isfile(f) or not os.access(f, os.R_OK):
            fail("Can't find or open sequence data")
    # print("File", f)
    if 'gz' in f:
        f = gzip.open(f, 'rt')
    else:
        f = open(f)

    tot = 0
    for line in f:
        line = line.strip()
        if 'Summary Targ' in line:
            tot += int(line.split()[2])
        elif 'Summary Near' in line:
            tot += int(line.split()[2])
        elif 'Targ' in line:
            dat = line.split()[1:]
            dat = [int(x) for x in dat]
            dat = tuple(dat)
            res[dat] = res.get(dat, 0) + 1

    print('barcode\tcount\tnorm')
    for spk in spks:
        c = res.get(spk, 0)
        r = c/tot if tot else 0.0
        print(f'{spk[0]}_{spk[1]}_{spk[2]}\t{c}\t{r}')
        #print(*spk,c,c/tot)

    for b1 in par[1]:
        for b2 in par[2]:
            for b3 in par[3]:
                c = res.get((b1,b2,b3), 0)
                r = c/tot if tot else 0.0
                print(f'{b1}_{b2}_{b3}\t{c}\t{r}')
                #print(b1,b2,b3,c,c/tot)


# def get_args():
#     runid, sample = sys.argv[1], sys.argv[2]
#     if not re.match("^\d{1,10}$", runid):
#         fail("Unexpected Run ID")
#     if not re.match("^[\w\.-]{1,20}$", sample):
#         fail("Unexpected Sample ID")
#     return(int(runid), sample)


def get_params(lay):
    # sth.execute("select lib from seqrun where runid = ?", (runid,))
    # lay = sth.fetchall()
    # lay = lay[0][0]
    if not lay: fail("Missing layout")

    sth.execute("select pos, bb from synth where sid = ? order by pos,bb", (lay,))
    bbk = sth.fetchall()
    if not bbk: fail("Missing BB assignments")
    for b in bbk:
        if not b[0] in par: par[b[0]] = list()
        par[b[0]].append(b[1])
    # print(par)


def fail(s):
    print("\n"+s)
    exit(0)


if __name__ == "__main__":
    main()

