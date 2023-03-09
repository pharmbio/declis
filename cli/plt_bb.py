#!/usr/bin/env python3
'''./bin/plt_bb.py library res_file(s)'''

# TODO: define lookup expected bb's to detect empties
# pre-define the dicts

# 101 111 122 43 0.0005071113522183173
# 101 111 123 97 0.0011439488643064369

import os, sys, sqlite3
import matplotlib.pyplot as plt

dbf = 'decl.db'
dbd = '../data'
dom = os.path.dirname(__file__)
dbd = dbd.split('/')
dbf = os.path.join(dom, *dbd, dbf)

if not os.path.isfile(dbf) or not os.access(dbf, os.R_OK):
    print("Database not found at %s" % dbf)
    exit(0)

dbh = sqlite3.connect(dbf)
sth = dbh.cursor()
dbh.set_trace_callback(print)

# runid = int(sys.argv[1])
# sth.execute("select lib from seqrun where runid = ?", (runid,))
# lay = sth.fetchall()
# lay = lay[0][0]
# if not lay: fail("Missing layout")

par = dict()
# sth.execute("select pos, bb from synth where sid = ? order by pos,bb", (lay,))
lay = int(sys.argv[1])
#libs = sys.argv[1].split(',')
#libs = list(map(int, libs))

sth.execute("select pos, bb from synth where sid = ? order by pos,bb", (lay,))
#sth.execute("select pos, bb from synth where sid in {} order by pos,bb".format(str(tuple(libs))))
#print(sth)
bbk = sth.fetchall()
if not bbk: fail("Missing BB assignments")
for b in bbk:
    if not b[0] in par: par[b[0]] = list()
    par[b[0]].append(b[1])


def main():
    for i in sys.argv[2:]:
        if not os.path.isfile(i) or not os.access(i, os.R_OK):
            fail("Can't open requested file '{}'".format(i))
        name = os.path.basename(i)[:-4]
        with open(i, 'rt') as f:
            bb1, bb2, bb3 = {}, {}, {}
            bb1 = {key: 0 for key in par[1]}
            bb2 = {key: 0 for key in par[2]}
            bb3 = {key: 0 for key in par[3]}
            # print(bb1)
            for line in f:
                if "4 4 4 " in line:
                    continue
                b1, b2, b3, n, r = line.split()
                b1 = int(b1)
                b2 = int(b2)
                b3 = int(b3)
                n = int(n)
                bb1[b1] = bb1.get(b1, 0) + n
                bb2[b2] = bb2.get(b2, 0) + n
                bb3[b3] = bb3.get(b3, 0) + n
            gen_plot(name, bb1, bb2, bb3)
            dump_txt(name, bb1, bb2, bb3)
            # print(bb1)

def gen_plot(name, bb1, bb2, bb3):
    plt.figure(figsize=(8,6))

    h = max(*bb1.values(), *bb2.values(), *bb3.values())
    # print(h)
    plt.xtics = []

    plt.subplot(311)
    (k, v) = zip(*bb1.items())
    plt.ylim(0,h)
    # x = range(0,max(k)+1,2)
    # plt.xticks(x)
    # plt.xlim(min(k),max(k))
    # print(name,min(k),max(k))
    plt.bar(k, v)

    plt.subplot(312)
    (k, v) = zip(*bb2.items())
    plt.ylim(0,h)
    plt.bar(k, v)

    plt.subplot(313)
    (k, v) = zip(*bb3.items())
    plt.ylim(0,h)
    plt.bar(k, v)

    plt.suptitle(name)
    #plt.ylabel('times seen')
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.35, wspace=0.35)

    plt.savefig("{}-bb.png".format(name))
    plt.close()

def dump_txt(name, bb1, bb2, bb3):
    i = 1
    for bb in (bb1, bb2, bb3):
        o = "{}-bb-{}.txt".format(name, i)
        i += 1
        with open(o, 'w') as f:
            for k,v in sorted(bb.items()):
                f.write("{}\t{}\n".format(k,v))

def fail(s):
    print("\n"+s)
    exit(0)


if __name__ == "__main__":
    #verbose = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    main()

