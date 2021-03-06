import sys
from sklearn.ensemble import *
from sklearn.svm import *
import argparse
import numpy
from scipy import sparse
from scipy.sparse import *
import math

parser=argparse.ArgumentParser(description='Train an svm and print out the svm feature weights - feature pair. Useful to examine the important features')
parser.add_argument('-i',help='input csv file',required=True)
parser.add_argument('-fea',help='csv file of feature names (one line), if not specified, col # (0 - feature number) will be used')
parser.add_argument('-pos',type=int,help='positive class label, required when class weight is used')
parser.add_argument('-neg',type=int,help='negative class label, required when class weight is used')
parser.add_argument('-pcw',type=float,help="positive class weight for svm")
parser.add_argument('-ncw',type=float,help="negative class weight for svm")
parser.add_argument('-cf',help="the file to be calssified, same format as the input csv")
parser.add_argument('-co',help="output classification result or not",action='store_true')
parser.add_argument('-pm',help="print model",action='store_true')
parser.add_argument('-s',help='sparse input, if the data set is sparse, use this option and will make svm much faster',action='store_true')
parser.add_argument('-libsvm',help='sparse input in libsvm format',action='store_true')

args,unknown = parser.parse_known_args(sys.argv)

if (args.pcw!=None or args.ncw!=None) and (args.pcw==None or args.ncw==None or args.pos==None or args.neg==None):
	print "if want to use class weight, pcw ncw pos neg parameters should all be specified"
	sys.exit(0)
if args.cf and (args.pos==None or args.neg==None):
	print "to classify file, use pos neg parameter"
	sys.exit(0)

def non_sparse(file_name):
	train=numpy.matrix(';'.join(open(file_name).read().splitlines()))
	[M,N]=train.shape
	test=numpy.asarray(train[:,0])
	train=train[:,1:N]
	return [train,test]

def sparse(file_name,max_fea=None):
	col=[]
        row=[]
        data=[]
	test=[]
        row_count=0
	f=open(file_name,'r')
        for line in f:
                s=line.split(',')
		test.append(float(s[0]))
                for i in range(1,len(s)):
                        if float(s[i])!=0:
                                col.append(i-1)
                                row.append(row_count)
                                data.append(float(s[i]))
		row_count+=1
	col_count=len(s)
	if max_fea==None:
		train=coo_matrix((data,(row,col)),shape=(row_count,col_count))
	else:
		train=coo_matrix((data,(row,col)),shape=(row_count,max_fea if max_fea>col_count else col_count))
	return [train,test]
def libsvm(file_name,max_fea=None):
	col=[]
        row=[]
        data=[]
	test=[]
        row_count=0
	f=open(file_name,'r')
        for line in f:
                s=line.split(' ')
		test.append(float(s[0]))
                for i in range(1,len(s)):
			ss=s[i].split(':')
                	col.append(int(ss[0]))
	                row.append(row_count)
        	        data.append(float(ss[1]))
		row_count+=1
	if max_fea==None:
		train=coo_matrix((data,(row,col)))
	else:
		train=coo_matrix((data,(row,col)),shape=(row_count,max_fea if max_fea>max(col)+1 else max(col)+1))
	return [train,test]
if not (args.s or args.libsvm):
	print "non-sparse input"
	[train,test]=non_sparse(args.i)
if args.s: #sparse input
	print "sparse input"
	[train,test]=sparse(args.i)
if args.libsvm: #sparse input
	print "libsvm input"
	[train,test]=libsvm(args.i,341473)
print train.shape

if args.pcw:
	model=LinearSVC(class_weight={args.pos:args.pcw,args.neg:args.ncw}).fit(train,test)
else:
	model=LinearSVC().fit(train,test)

if args.pm:
	para=model.coef_[0]
	print len(para)
	if args.fea:
		fea=list(open(args.fea,'r').read().strip().splitlines())
		print len(fea)
		if len(para)!=len(fea):
			print "the feature names should be the same length with the feature vector you passed into svm"
			sys.exit(0)
	if args.fea:
		zipped=zip(para,fea)
	else:
		zipped=zip(para,range(0,len(para)))
	zipped.sort(key = lambda t: abs(t[0]),reverse=True)
	for pair in zipped:
		print str(pair[0])+","+str(pair[1])

[M,N]=train.shape

if args.cf:	
	if not (args.s or args.libsvm):
		[train,y_test]=non_sparse(args.cf)
	elif args.s:
		[trai,y_test]=sparse(args.cf,N)
	elif args.libsvm:
		[train,y_test]=libsvm(args.cf,N)
	y_test=numpy.asarray(y_test)
	print train.shape
	p_test=model.predict(train)
	if args.co:
		for i in p_test:
			print i
	tp=0
	tn=0
	fp=0
	fn=0
	for i in range(0,len(p_test)):
		if p_test[i]==args.pos and y_test[i]==args.pos:
			tp+=1
		elif p_test[i]==args.pos and y_test[i]==args.neg:
			fp+=1
		elif p_test[i]==args.neg and y_test[i]==args.neg:
			tn+=1
		elif p_test[i]==args.neg and y_test[i]==args.pos:
			fn+=1
		else:
			print 'error'
	if tp==0:
		pre=0
		rec=0
	else:
		pre=float(tp)/(tp+fp)
		rec=float(tp)/(tp+fn)
	acc=float(tp+tn)/(tp+fn+fp+tn)
	if pre==0 and rec==0:
		f1=0
	else:
		f1=2*pre*rec/(pre+rec)
	print 'precision\trecall\taccuracy\tf1-score'
	print str(pre)+'\t'+str(rec)+'\t'+str(acc)+'\t'+str(f1)
	print 'tp\tfp\ttn\tfn'
	print str(tp)+'\t'+str(fp)+'\t'+str(tn)+'\t'+str(fn)
