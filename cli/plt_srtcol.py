#!/usr/bin/env python3
'''./bin/plotres.py column res_file(s)'''
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
            for line in f:
                if line[0] == 'b': continue
                data.append(float(line.split()[col]))
            pvar = 1; #pvariance(data)
            data.sort(reverse=True)
            gen_plot(name, pvar, data)

def gen_plot(name, pvar, data):
    plt.plot(data, 'b.')
    plt.title(name)
    #plt.xlabel('var = {}'.format(pvar))
    plt.ylabel('times seen')
    plt.savefig("{}.png".format(name))
    plt.close()

def fail(s):
    print("\n"+s)
    exit(0)


if __name__ == "__main__":
    #verbose = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    main()
