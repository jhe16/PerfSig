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

import datetime

from time import time as tm

start = tm()

workloadstart = 1611939893000 # 12:04:53
workloadend = 1611939980000 # 12:06:20

bugtrigger = 1611939958000 # 12:05:58

interval = 1000 # sampling interval 1s

#read log sequence
with open('logseq-11252.pickle', 'rb') as handle:
    logseq = pickle.load(handle)

# read function call time vector
with open('functimevector-11252.pickle', 'rb') as handle:
    functimevec = pickle.load(handle)

timevector = []
names = []
idx = 0
causenum = 0
compnum = 0
for func in functimevec:
    timevector.append(functimevec[func])
    names.append(func)
    if func == 'hadoop11252':
        causenum = idx
    if func == 'org.apache.hadoop.hdfs.protocol.ClientProtocol.create':
        compnum = idx

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
    print("person coefficient: %.4f " % (abs(pvalue)))
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
    print("Spearmans correlation: %.4f " % (abs(corr)))
    corrresult.append(abs(corr))
npresult = np.array(corrresult)
sortidx = np.argsort(npresult)
avg = np.average(corrresult)

for i in range(len(sortidx)):
    if sortidx[i] == causenum:
        break
print ('the rank of root cause function is: ' + str(len(sortidx) - i))
print ('xx percent higher than average: ' + str((corrresult[causenum]/avg - 1) * 100))

timeline=list(range(workloadstart, workloadend, interval))
realtime = []
for dt in timeline:
    t = datetime.datetime.fromtimestamp(int(dt/1000))
    print ('converted time: ')
    print (t)
    tmp = str(t.hour) + ':0' + str(t.minute) + ':' + str(t.second)
    print (tmp)
    realtime.append(tmp)

end = tm()
print ('causal analysis time: ')
print (end - start)

tick_spacing = 20
fig, ax = plt.subplots(1,1)
# ax.plot(realtime, logseq, color = 'b', label = 'log sequence', linewidth=2)
# ax.legend(('Log sequence execution time'), loc='best')
ax.plot(realtime, timevector[causenum], 'b', label = 'RPC.waitForProtocolProxy', linewidth=2)
ax.plot(realtime, timevector[compnum], 'r-.', label = 'ClientProtocol.create', linewidth=2)
plt.axvline(x=65, linestyle='--', label = 'bug start time', linewidth=5)
# ax.legend(loc='best', fontsize=25)
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.set_xlabel("Time (s)", fontsize=25)
ax.set_ylabel("Function time span (ms)", fontsize=20)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width, box.height * 0.5])
legend = ax.legend(loc='center left', bbox_to_anchor=(0.1, 1.2), ncol=2)
plt.setp(plt.gca().get_legend().get_texts(), fontsize='25')

# plt.tight_layout()

plt.show()






