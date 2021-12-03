import matplotlib.pyplot as plt
import csv
import pickle

workloadstart = 1620397931000   #10:32:11 
bugtrigger = 1620397982000    #10:33:02
bugend = 1620398048000      #10:34:08
workloadend = 1620398048000    #10:34:08

# f = open("htrace.out")
f = open("15415.out")
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
timevector["hadoop15415"] = [0 for _ in range(duration)]
while time < bugend:
    cnt = int((time - workloadstart) / interval)
    timevector["hadoop15415"][cnt] += interval
    time += interval


for funcname in timevector:
    print (funcname)
    print (timevector[funcname])

with open('functimevector-15415.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)


   







