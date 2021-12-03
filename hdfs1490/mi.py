import matplotlib.pyplot as plt
import csv
import pickle
from sklearn import linear_model
from scipy import signal
from jpype import *
import random
import math
from sklearn import metrics
from sklearn.preprocessing import normalize
import numpy as np
import matplotlib.ticker as ticker
from scipy.stats import pearsonr
from scipy.stats import spearmanr

from time import time as tm

start = tm()

workloadstart = 1619198329000 # 13:18:49
workloadend = 1619198410000 # 13:20:10

interval = 1000 # sampling interval 1s

#read log sequence
with open('logseq-1490.pickle', 'rb') as handle:
    logseq = pickle.load(handle)

# read function call time vector
with open('functimevector-1490.pickle', 'rb') as handle:
    functimevec = pickle.load(handle)

timevector = []
names = []
idx = 0
causenum = 0
for func in functimevec:
    timevector.append(functimevec[func])
    names.append(func)
    if func == 'org.apache.hadoop.hdfs.server.namenode.testGetImaageTimeout':
        causenum = idx
    idx += 1

print ("number of invoked functions: " + str(len(timevector)))
print ("number of invoked functions: " + str(idx))
print ("index of root cause functions: " + str(causenum))



#transfer entropy

#normalize data

def normalization(inputlist):
    tmp = np.array(inputlist)
    norm = normalize(tmp[:,np.newaxis], axis=0).ravel()
    return norm

funccause = []
funcname = []
for j in range(len(timevector)):
    funcname.append(names[j])
    cause = []
    for i in timevector[j]:
        cause.append(int(i))
    funccause.append(normalization(cause))


lognorm = normalization(logseq)

print (len(funcname))
print (len(funccause))
print (len(funccause[0]))
print (len(lognorm))

result = []


# mutual information
for cause in funccause: 
    subresult = metrics.normalized_mutual_info_score(cause, lognorm)
    print("Mutual information: %.4f " % (subresult))
    result.append(float(subresult))
npresult = np.array(result)
sortidx = np.argsort(npresult)
print ('the ranked causality is: ')
print (np.sort(result))
avg = np.average(result)

for i in range(len(sortidx)):
    if sortidx[i] == causenum:
        break
print ('the rank of root cause function is: ' + str(len(sortidx) - i))
print ('xx percent higher than average: ' + str((result[causenum]/avg - 1) * 100))

#person coefficient
pvalueresult = []
for cause in funccause: 
    pvalue, _ = pearsonr(cause, lognorm)
    # print("person coefficient: %.4f " % (abs(pvalue)))
    pvalueresult.append(abs(pvalue))
npresult = np.array(pvalueresult)
sortidx = np.argsort(npresult)
avg = np.average(pvalueresult)

for i in range(len(sortidx)):
    if sortidx[i] == causenum:
        break
print ('the rank of root cause function is: ' + str(len(sortidx) - i))
print ('xx percent higher than average: ' + str((pvalueresult[causenum]/avg - 1) * 100))

# calculate spearman's correlation
corrresult = []
for cause in funccause: 
    corr, _ = spearmanr(cause, lognorm)
    # print("Spearmans correlation: %.4f " % (abs(corr)))
    corrresult.append(abs(corr))
npresult = np.array(corrresult)
sortidx = np.argsort(npresult)
avg = np.average(corrresult)

for i in range(len(sortidx)):
    if sortidx[i] == causenum:
        break
print ('the rank of root cause function is: ' + str(len(sortidx) - i))
print ('xx percent higher than average: ' + str((corrresult[causenum]/avg - 1) * 100))

end = tm()
print ('causal analysis time: ')
print (end - start)

timeline=list(range(workloadstart, workloadend, interval))
tick_spacing = 15000
fig, ax = plt.subplots(1,1)
ax.plot(timeline, logseq, color = 'b', label = 'Log sequence')
# ax.legend(('Log sequence execution time'), loc='best')
ax.plot(timeline, timevector[causenum], color = 'r', label = 'root cause function')
ax.legend(fontsize=20)
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.set_xlabel("Timestamp", fontsize=30)
ax.set_ylabel("Time vectors (ms)", fontsize=30)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.show()






