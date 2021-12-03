import matplotlib.pyplot as plt
import csv
import pickle

workloadstart = 1620344606000   #19:43:26
bugtrigger = 1620344656000    #19:44:16
bugend = 1620344731000       #19:45:31
workloadend = 1620344731000    #19:45:31

# f = open("htrace.out")
f = open("7089.out")
lines = f.readlines()
starttime = []
functionname = []
executiontime = []

for line in lines:
    if "\"d\":" in line:
        linesplit = line.split(",\"")
        if " " not in linesplit[4] and int(linesplit[2].split(":")[1]) > workloadstart:
            func = linesplit[4].split(":")
            funcname = eval(func[1])
            start = int(linesplit[2].split(":")[1])
            elapsed = int(linesplit[3].split(":")[1]) - start
            if (elapsed == 0):
                elapsed = 1
            print (funcname)
            print (start)
            print (elapsed)
            functionname.append(funcname)
            starttime.append(start)
            executiontime.append(elapsed)


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
timevector["mapreduce7089"] = [0 for _ in range(duration)]
while time < bugend:
    cnt = int((time - workloadstart) / interval)
    timevector["mapreduce7089"][cnt] += interval
    time += interval


for funcname in timevector:
    print (funcname)
    print (timevector[funcname])

with open('functimevector-7089.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)


   







