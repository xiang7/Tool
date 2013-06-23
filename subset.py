#performs a random sample from a file
import argparse
import sys
import codecs
import random
import subprocess

parser=argparse.ArgumentParser(description='Performs a random sample from a file')
parser.add_argument('-ns',help='not shuffling the output',action='store_true')
parser.add_argument('-i',help='input file to be sampled',required=True,type=str)
parser.add_argument('-n',help='number of lines to be sampled',type=int)
parser.add_argument('-p',help='portion of lines to be sampled',type=float)
args,unknown=parser.parse_known_args(sys.argv)
if not args.n and not args.p:
    parser.exit(2,'at least one of -n or -p should be specifie\n')
if args.n and args.p:
    parser.exit(2,'-n and -p can not both exist\n')
f=codecs.open(args.i,'r','UTF-8');
if not args.p:
    t_l=int(subprocess.check_output(['wc -l '+args.i],shell=True).split()[0])
    prob=float(args.n)/float(t_l)
else:
    prob=args.p

count=0
total=0

if args.ns and args.p:
    for line in f:
        total+=1;
        if random.random()<prob:
	    print line.strip()
	    count+=1
    f.close();
else:
    prob=prob*1.1
    rec=[]
    for line in f:
	total+=1
        if random.random()<prob:
	    rec.append(line.strip())
	    count+=1
    f.close();
    if not args.ns:
	random.shuffle(rec)
	if args.n:
	    for s in rec[0:args.n]:
		print s.strip()
	else:
	    for s in rec[0:int(len(rec)/1.1)]:
		print s.strip()
    else:
	for s in rec[0:args.n]:
	    print s.strip()
