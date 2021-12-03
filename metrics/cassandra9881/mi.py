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

from time import time as tme

start = tme()

workloadstart = 1621020389000   #15:26:29
bugtrigger = 1621020451000    #11:27:31
bugend = 1621020540000      #15:29:00
workloadend = 1621020540000    #15:29:00


cutstart = int((bugtrigger - workloadstart)/1000)
cutend = int((workloadend - bugtrigger)/1000)

#read CPU utilization
cpu = []
time = []
with open('9881-cpu.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            # print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            print(f'\t{row[1]}')
            cpu.append(float(row[1]))
            time.append(row[0])
            line_count += 1


triggertime = int((bugtrigger - workloadstart) / 1000) 

cpuepisode = cpu[(triggertime-cutstart) : (triggertime+cutend)]

timeline = time[(triggertime-cutstart) : (triggertime+cutend)]

#filter noise
b, a = signal.butter(3, 0.1)
# b, a = signal.butter(3, 0.7, btype='highpass')
cpufigure = signal.filtfilt(b, a, cpuepisode)
# cpufigure = cpuepisode

#calculate slope of CPU
cpuslope = []
for i in range(len(cpufigure)-1):
    cpuslope.append(cpufigure[i+1] - cpufigure[i])
cpuslope.append(cpuslope[-1])
    

#read time vector
with open('functimevector-9881.pickle', 'rb') as handle:
    functimevector = pickle.load(handle)

timevector = []
names = []
idx = 0
causenum = 0
for func in functimevector:
    timevector.append(functimevector[func])
    names.append(func)
    if func == 'cassandra9881':
        causenum = idx
    idx += 1

causefuncfigure = timevector[causenum][triggertime-cutstart:triggertime+cutend]

print ("number of invoked functions: " + str(len(timevector)))
print ("number of invoked functions: " + str(idx))
print ("index of root cause functions: " + str(causenum))

timevectorcut = []
for vector in timevector:
    timevectorcut.append(vector[triggertime-cutstart:triggertime+cutend])


#transfer entropy

#normalize data

def normalization(inputlist):
    tmp = np.array(inputlist)
    norm = normalize(tmp[:,np.newaxis], axis=0).ravel()
    return norm

funccause = []
funcname = []
for j in range(len(timevectorcut)):
    # if sum(timevectorcut[j]) > 0:
    funcname.append(names[j])
    cause = []
    for i in timevectorcut[j]:
        cause.append(int(i))
    funccause.append(normalization(cause))


cpuchange = []
# for uti in cpuslope:
for uti in cpufigure:
    cpuchange.append(int(uti))

cpunorm = normalization(cpuchange)
# print (cpuchange)
# print (cpunorm)

print (len(funcname))
print (len(funccause))
print (len(funccause[0]))
print (len(cpuchange))

result = []

# mutual information
for cause in funccause: 
    subresult = metrics.normalized_mutual_info_score(cause, cpunorm)
    print("Mutual information: %.4f " % (subresult))
    result.append(float(subresult))
npresult = np.array(result)
sortidx = np.argsort(npresult)
avg = np.average(result)

for i in range(len(sortidx)):
    if sortidx[i] == causenum:
        break
print ('the rank of root cause function is: ' + str(len(sortidx) - i))
print ('xx percent higher than average: ' + str((result[causenum]/avg - 1) * 100))

#person coefficient
pvalueresult = []
for cause in funccause: 
    pvalue, _ = pearsonr(cause, cpunorm)
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
    corr, _ = spearmanr(cause, cpunorm)
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

end = tme()
print ('causal analysis time: ')
print (end - start)

tick_spacing = 40
fig, ax = plt.subplots(1,1)
ax.plot(timeline, cpuepisode, color = 'b')
ax.plot(timeline, cpufigure, color = 'hotpink')
ax.plot(timeline, cpuslope, color = 'r')
# ax.plot(timeline, causefuncfigure, color = 'r')
# plt.axvline(x=cutstart, linestyle='--')
ax.legend(('CPU utilization', 'filtered CPU utilization', 'CPU slope'), loc='best')
# ax.legend(('CPU utilization', 'filtered CPU utilization' , 'CPU slope' , 'bug triggering time'), loc='best')
# ax.legend(['root cause function (cassandra-9881)'])
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.set_xlabel("Time(s)")
ax.set_ylabel("CPU utilization")
# ax.set_ylabel("Time vectors of functions")
plt.show()




