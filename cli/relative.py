#!/usr/bin/env python3
'''./bin/enrank2.py standard candidate(s)'''
# outputs merged bc but still takes separated bc input
# todo: drop multifile support

import os, sys

def main():
    files  = []
    enrich = []
    # header = ['b1','b2','b3']
    header = ['barcode']
    data   = []
    outf   = []

    for i,f in enumerate(sys.argv[1:],start=0):
        if not os.path.isfile(f) or not os.access(f, os.R_OK):
            fail("Can't open requested file '{}'".format(f))
        files.append(open(f, 'rt'))
        f = os.path.basename(f)
        f = os.path.splitext(f)[0]
        #outf.append(f)
        #header.append(f+'_n')
        header.extend([f+'_c', f+'_n'])
        if i:
            #header.extend([f+'_e', f+'_r'])
            header.append(f+'_r')
            enrich.append([])
            outf.append(f)
    outf = '_'.join(outf) + '.cmp'
    outf = open(outf, 'w')
    # print(*header)
    header = '\t'.join(header) +'\n'
    outf.write(header)

    i = 0
    for line in files[0]:
        line = line.strip()
        (b1,b2,b3,n,e) = line.split()
        #n = int(n)
        e = float(e)
        if not e: e = 1/1e5
        # data.append([b1,b2,b3,n,e])
        bc = '_'.join((b1,b2,b3))
        data.append([bc,n,e])

        j = 0
        for f in files[1:]:
            # vn, ve = f.readline().strip().split()[3:5]
            line = f.readline().strip()
            if len(line) < 3:
                print(f"Skipping empty file {f.name}")
                exit(0)
            # v1, v2, v3, vn, ve = f.readline().strip().split()
            v1, v2, v3, vn, ve = line.split()
            if (v1,v2,v3) == ('4','4','4'): 
                v1, v2, v3, vn, ve = f.readline().strip().split()
            bc = '_'.join((v1,v2,v3))
            assert bc == data[i][0]
            # vn = int(vn)
            ve = float(ve)
            data[i].extend([vn,ve/e])
            enrich[j].append(ve/e)
            j += 1
        i += 1

    for i in range(len(enrich)):
        j = enrich[i]
        r = rankdata(j)
        r = [int(x)for x in r]
        enrich[i] = r

    for i,d in enumerate(data):
        e = []
        for j in enrich:
            e.append(j[i])
        #print(*d,*e)
        ut = [str(x) for x in d+e]
        ut = '\t'.join(ut) + '\n'
        outf.write(ut)
        #if i > 5: break


def fail(s):
    print("\n"+s)
    exit(0)

def rank_simple(vector):
    return sorted(range(len(vector)), key=vector.__getitem__, reverse=True)

def rankdata(a):
    n = len(a)
    ivec=rank_simple(a)
    svec=[a[rank] for rank in ivec]
    sumranks = 0
    dupcount = 0
    newarray = [0]*n
    for i in range(n):
        sumranks += i
        dupcount += 1
        if i==n-1 or svec[i] != svec[i+1]:
            averank = sumranks / float(dupcount) + 1
            for j in range(i-dupcount+1,i+1):
                newarray[ivec[j]] = averank
            sumranks = 0
            dupcount = 0
    return newarray

if __name__ == "__main__":
    #verbose = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    main()
    pass
