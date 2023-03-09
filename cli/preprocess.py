#!/usr/bin/env python3
'''preprocess.py lib_id fastq_data'''

import os, re, sys
import gzip, sqlite3
import argparse

miq =  30            # minimum quality value in fastq input
fel =  0             # max errors allowed in critical seq positions
db_rel = '../data'   # location of sqlite db file relative to script
db_fil = 'decl.db'
fq_dir = './'
par = dict()         # will hold library-specific parameters

# could/should make more of the above into options
parser = argparse.ArgumentParser()
parser.add_argument("libid", type=int, help="DECL library type (integer)")
parser.add_argument("fastq", help="DECL sequence data (compressed fastq)")
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
else:
    print(f"Using db at {dbf}")

# should wrap with catch, etc
dbh = sqlite3.connect(dbf)
sth = dbh.cursor()

# grab the entire building block collection to ease error tracking
sth.execute("select bc,oid from d3bc")
bb = sth.fetchall()
bb = dict(bb)


def main():
    # check for overflow of qual sum?
    j, q, n, s = 0, 0, 0, 0
    Qual, Fail, Miss, Near, Targ, stat = 0, 0, 0, 0, 0, ''
    libid, sample = args.libid, args.fastq
    
    get_params(libid)

    f = fq_dir + sample + '.fq'
    if not os.path.isfile(f) or not os.access(f, os.R_OK):
        f += '.gz'
        if not os.path.isfile(f) or not os.access(f, os.R_OK):
            fail("Can't find or open sequence data")

    print("File", f)
    hack = 0
    if 'gz' in f:
        f = gzip.open(f, 'rt')
    else:
        f = open(f)
    for line in f:
        line = line.strip() #; print(line)
        if j == 1:
            seq = line
            n += 1
            if hack and n > hack: break
        if j == 3:
            q = ave_qual(line)
            s += q
            if q < miq:
                Qual += 1
                print("Qual", q)
            else:
                seq_test = chk_seq(seq)
                if 0 in seq_test:
                    Fail += 1
                    print("Fail", *seq_test, n)
                else:
                    found = parse_seq(seq, seq_test[0])
                    #found[0], found[1], found[2:]
                    if found[0]:
                        Miss += 1
                        stat = 'Miss'
                    elif found[1]:
                        Near += 1
                        stat = 'Near'
                    else:
                        Targ += 1
                        stat = 'Targ'
                    print(stat, *found[2:])
        j += 1
        j %= 4
    print('Summary Seqs', n)
    print('Summary Targ', Targ, Targ/n)
    print('Summary Near', Near, Near/n)
    print('Summary Miss', Miss, Miss/n)
    print('Summary Fail', Fail, Fail/n)
    print('Summary Qual', Qual, Qual/n)
    print('Summary AveQ', s/n)



def parse_seq(seq, direction):
    hits = [0, 0]
    off = 0 if direction == 1 else 2
    bb1 = par['bb1'][1+off]
    bb2 = par['bb2'][1+off]
    bb3 = par['bb3'][1+off]
    for i,b in enumerate((bb1, bb2, bb3), start=1):
        s = seq[b:b+8] # fix this hardcoded value
        if s not in bb:
            hits[0] += 1
            hits.append(0)
        else:
            hits.append(bb[s])
            if bb[s] not in par[i]:
                hits[1] += 1
    # if hits[2:] == spk:
    #     hits[1] = 0
    if hits[2] and hits[2] < 100 and hits[3] and hits[3] < 100 and hits[4] and hits[4] < 100:
        hits[1] = 0
    return hits


def chk_seq(seq):
    seq_test = []
    direction = chk_head(seq)
    seq_test.append(direction)
    # if not direction: return None
    seq_test.append(chk_tail(seq, direction))
    for chk in ('lib','L0','L1','L2','L3'):
        seq_test.append(chk_tag(seq, chk, direction))
    return(seq_test)


def chk_tag(seq, tag, direction):
    err = 0
    off = 0 if direction == 1 else 2
    t = par[tag][off]
    p = par[tag][off + 1]
    s = seq[p:]

    for i in range(len(t)):
        err += t[i] != s[i]
        if err > fel:
            return 0
    return 1


def chk_tail(seq, direction):
    err = 0
    if direction == 1:
        t = par['tail'][0]
        p = par['tail'][1]
    elif direction == 2:
        t = par['head'][2]
        p = par['tail'][3]
    else:
        return 0
    s = seq[p:]
    for i in range(len(t)):
        err += t[i] != s[i]
    if err > fel:
        return 0
    else:
        return direction


def chk_head(seq):
    ferr, rerr = 0, 0
    fwd = par['head'][0]; rev = par['tail'][2]
    for i in range(len(fwd)):
        ferr += fwd[i] != seq[i]
        rerr += rev[i] != seq[i]
    if ferr > fel and rerr > fel:
        return 0
    elif ferr <= fel:
        return 1
    elif rerr <= fel:
        return 2


def get_params(lay):
    ''' shameful use of a global '''

    # sth.execute("select lib from seqrun where runid = ?", (runid,))
    # lay = sth.fetchall()
    # lay = lay[0][0]
    if not lay: fail("Missing layout")

    sth.execute("select tag, seq, pfwd, prev from layout where lay = ?", (lay,))
    tags = sth.fetchall()
    if not tags: fail("Missing sample parameters")
    for t in tags:
        par[t[0]] = (t[1],t[2],revcomp(t[1]),t[3])

    sth.execute("select pos, bb from synth where sid = ? order by pos,bb", (lay,))
    bbk = sth.fetchall()
    if not bbk: fail("Missing BB assignments")
    for b in bbk:
        if not b[0] in par: par[b[0]] = list()
        par[b[0]].append(b[1])

    if verbose:
        print(par)
        print('BB2', par['bb2'], par[2])


# check at specific positions?
def ave_qual(s):
    # assuming Illumina (eg, phred-33)
    t=0
    for q in s:
        t += ord(q)
    return(t/len(s) - 33)


# def get_bb(strand, seq):
#     err = 0
#     for i in range(len(pri)):
#         err += pri[i] != seq[i]
#         if err > fel:
#             return 0
#     return 1


def revcomp(seq):
    comp = {'A' : 't', 'C' : 'g', 'T' : 'a', 'G' : 'c'}
    for base in comp.keys():
        seq = seq.replace(base,comp[base])
    return seq.upper()[::-1]


def fail(s):
    print("\n"+s)
    exit(0)


if __name__ == "__main__":
    main()
