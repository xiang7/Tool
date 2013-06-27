#author: Luojie Xiang
import sys
from sklearn.ensemble import *
import numpy
from sklearn import cross_validation
from sklearn.svm import *
from sklearn.metrics import f1_score
from sklearn import metrics
import argparse

parser=argparse.ArgumentParser(description='Cross validation on a preprocessed dataset (for binary classification). Input format: csv, each line a data sample, the first column is the label and the rest are numerical values for each feature.')
parser.add_argument('-i',help='input csv file',required=True)
parser.add_argument('-pos',type=int,help='positive label (int)',required=True)
parser.add_argument('-neg',type=int,help='negative label (int)',required=True)
parser.add_argument('-fold',type=int,help='number of folds, default 10')
parser.add_argument('-c',help='classifier type, default svm or rf (RandomForestClassifier)')

args,unknown = parser.parse_known_args(sys.argv)
pos=args.pos
neg=args.neg
fold=10
if args.fold:
	fold=args.fold
classifier='svm'
if args.c:
	classifier=args.classifier.lower().strip()

train=numpy.matrix(';'.join(open(args.i).read().splitlines()))
[M,N]=train.shape
test=train[:,0]
train=train[:,1:N]
pre=0.0
rec=0.0
acc=0.0
print 'tp\tfn\ttn\tfp'
for i in range(0,fold):
	x_train,x_test,y_train,y_test=cross_validation.train_test_split(train,test,test_size=1.0/float(fold))
	if classifier=='svm':
		model=LinearSVC().fit(x_train,y_train)
	elif classifier=='rf':
		model=RandomForestClassifier().fit(x_train,y_train)
	p_test=model.predict(x_test)
	tp=0
	tn=0
	fp=0
	fn=0
	for i in range(0,len(p_test)):
		if p_test[i]==pos and y_test[i]==pos:
			tp+=1
		elif p_test[i]==pos and y_test[i]==neg:
			fp+=1
		elif p_test[i]==neg and y_test[i]==neg:
			tn+=1
		elif p_test[i]==neg and y_test[i]==pos:
			fn+=1
		else:
			print 'error'
	if tp==0:
		pre_temp=0
		rec_temp=0
	else:
		pre_temp=float(tp)/(tp+fp)
		rec_temp=float(tp)/(tp+fn)
	acc_temp=float(tp+tn)/(tp+fn+fp+tn)
	pre+=pre_temp
	rec+=rec_temp
	acc+=acc_temp
	print str(tp)+'\t'+str(fn)+'\t'+str(tn)+'\t'+str(fp)
if pre==0 and rec==0:
	f1=0
else:
	f1=2*pre/fold*rec/fold/(pre/fold+rec/fold)
print 'precision\trecall\taccuracy\tf1-score'
print str(pre/fold)+'\t'+str(rec/fold)+'\t'+str(acc/fold)+'\t'+str(f1)
