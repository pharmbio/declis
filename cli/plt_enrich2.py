#!/usr/bin/env python3
'''./bin/plt_enrich2.py 7 cmp_file(s)'''
import os, sys
import matplotlib.pyplot as plt
#from statistics import pvariance

def main():
    col = int(sys.argv[1]) - 1
    for i in sys.argv[2:]:
        if not os.path.isfile(i) or not os.access(i, os.R_OK):
            fail("Can't open requested file '{}'".format(i))
        name = os.path.basename(i)[:-4]
        with open(i, 'rt') as f:
            data = list()
            base = list()
            for line in f:
                if line[0] == 'b': continue
                data.append(float(line.split()[col]))
                # base.append(int(line.split()[3]))
                base.append(int(line.split()[1]))  # merged barcodes
            # pvar = 1; #pvariance(data)
            data.sort(key=dict(zip(data,base)).get)
            # gen_plot(name, pvar, data)
            gen_plot(name, data)

def gen_plot(name, data):
    plt.plot(data, 'b.')
    plt.title(name)
    plt.xlabel('pre-selection rank')
    plt.ylabel('enrichment')
    plt.savefig("{}-s.png".format(name))
    plt.close()

def fail(s):
    print("\n"+s)
    exit(0)


if __name__ == "__main__":
    #verbose = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    main()
