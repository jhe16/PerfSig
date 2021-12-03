import matplotlib.pyplot as plt
import csv
import pickle

workloadstart = 1620413330000   #14:48:50
bugtrigger = 1620413419000     #14:50:19
bugend = 1620413454000         #14:50:54
workloadend = 1620413529000    #14:52:09

# f = open("htrace.out")
f = open("6133.out")
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
    while time < starttime[i] + executiontime[i]:
        cnt = int((time - workloadstart) / interval)
        timevector[funcname][cnt] += min(starttime[i] + executiontime[i], (cnt + 1) * interval + workloadstart) - time
        time = (cnt + 1) * interval + workloadstart

    # timevector[funcname][cnt] += executiontime[i]


# #constructing function time vector
# interval = 1000  #sampling interval 1s
# timevector = {}
# duration = int((workloadend - workloadstart) / interval)

# for i in range(len(starttime)):

#     if (starttime[i] >= workloadend) or starttime[i] < workloadstart:
#         continue

#     funcname = functionname[i]
#     if funcname not in timevector:
#         timevector[funcname] = [0 for _ in range(duration)]

#     cnt = int((starttime[i] - workloadstart) / interval)

#     time = starttime[i]
#     while time < starttime[i] + executiontime[i]:
#         cnt = int((time - workloadstart) / interval)
#         timevector[funcname][cnt] += min(starttime[i] + executiontime[i], (cnt + 1) * interval + workloadstart) - time
#         time = (cnt + 1) * interval + workloadstart

#     # timevector[funcname][cnt] += executiontime[i]

# #bug injection
# time = bugtrigger
# timevector["hadoop6133"] = [0 for _ in range(duration)]
# while time < bugend:
#     cnt = int((time - workloadstart) / interval)
#     timevector["hadoop6133"][cnt] += interval
#     time += interval


for funcname in timevector:
    print (funcname)
    print (timevector[funcname])

with open('functimevector-6133.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)


   







