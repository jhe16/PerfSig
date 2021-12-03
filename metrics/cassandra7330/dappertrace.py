import matplotlib.pyplot as plt
import csv
import pickle
import json

workloadstart = 1621005713000   #11:21:53
bugtrigger = 1621005780000    #11:23:00
bugend = 1621005840000      #11:24:00
workloadend = 1621005840000    #11:24:00

starttime = []
functionname = []
executiontime = []

filelist = ['8afdc9386cbe5679.json', '430be2643f7ffb4e.json', '9359c6f6159ed4af.json', 'ac0eb283b8609bff.json', 'c306fd8eb753a088.json']

dictlist = []
for fpath in filelist:
    with open(fpath,'r') as load_f:
        load_dict = json.load(load_f)
        dictlist.append(load_dict)

for load_dict in dictlist:
    for t in load_dict:
        print (t)
        print (t['name'])
        functionname.append(t['name'])
        print (t['timestamp'])
        starttime.append(int(t['timestamp']/1000))
        print (t['duration'])
        dur = int(t['duration']/1000)
        if dur == 0:
            dur = 1
        executiontime.append(dur)

#constructing function time vector
interval = 1000  #sampling interval 1s
timevector = {}
duration = int((workloadend - workloadstart) / interval)

for i in range(len(starttime)):

    if starttime[i] >= workloadstart + duration * interval:
        continue

    funcname = functionname[i]
    if funcname not in timevector:
        timevector[funcname] = [0 for _ in range(duration)]

    cnt = int((starttime[i] - workloadstart) / interval)

    timevector[funcname][cnt] += executiontime[i]


#bug injection
time = bugtrigger
timevector["cassandra7330"] = [0 for _ in range(duration)]
while time < bugend:
    cnt = int((time - workloadstart) / interval)
    timevector["cassandra7330"][cnt] += interval
    time += interval


for funcname in timevector:
    print (funcname)
    print (timevector[funcname])

with open('functimevector-7330.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)


   







