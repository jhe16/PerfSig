import matplotlib.pyplot as plt
import csv
import pickle
import json

workloadstart = 1621020389000   #15:26:29
bugtrigger = 1621020451000    #11:27:31
bugend = 1621020540000      #15:29:00
workloadend = 1621020540000    #15:29:00

starttime = []
functionname = []
executiontime = []

filelist = ['355dcf4bed46d91d.json', 'cb293c850a40fa8b.json', '7f30fbe7efa571ee.json', 'ef6bbc17190538f4.json', 'c612bef1de84159e.json']

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
timevector["cassandra9881"] = [0 for _ in range(duration)]
while time < bugend:
    cnt = int((time - workloadstart) / interval)
    timevector["cassandra9881"][cnt] += interval
    time += interval


for funcname in timevector:
    print (funcname)
    print (timevector[funcname])

with open('functimevector-9881.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)


   







