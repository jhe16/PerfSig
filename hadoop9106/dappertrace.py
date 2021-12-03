import matplotlib.pyplot as plt
import csv
import pickle

workloadstart = 1617984807000 # 12:13:27
workloadend = 1617984860000 # 12:14:20

f = open("9106.out")
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
            # print (funcname)
            # print (start)
            # print (elapsed)
            functionname.append(funcname)
            starttime.append(start)
            executiontime.append(elapsed)


#constructing function time vector
interval = 1000  # sampling interval 1s
timevector = {}
duration = int((workloadend - workloadstart) / interval)

for i in range(len(starttime)):

    if (starttime[i] >= workloadend) or starttime[i] < workloadstart:
        continue

    funcname = functionname[i]
    if funcname not in timevector:
        timevector[funcname] = [0 for _ in range(duration)]

    cnt = int((starttime[i] - workloadstart) / interval)

    time = starttime[i]
    while time < starttime[i] + executiontime[i] and time < workloadend:
        cnt = int((time - workloadstart) / interval)
        timevector[funcname][cnt] += min(starttime[i] + executiontime[i], (cnt + 1) * interval + workloadstart) - time
        time = (cnt + 1) * interval + workloadstart

    # timevector[funcname][cnt] += executiontime[i]



for funcname in timevector:
    print (funcname)
    print (timevector[funcname])

with open('functimevector-9106.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)


   







