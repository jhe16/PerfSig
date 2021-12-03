import matplotlib.pyplot as plt
import csv
import matplotlib.ticker as ticker

f = open("hadoop6133-workload.txt")
lines = f.readlines()
timepoint = []
cpuusage = []
for line in lines:
#    print line
    if line.count(":", 0, len(line)) == 2:
    	timepoint.append(line[:-1])
    # if "cpu utilization:" in line:
    if "cpu utilization:" in line:
    	linesplit = line.split(": ")
    	print (linesplit[1])
    	cpuusage.append(float(linesplit[1][:-2]))

f.close()
 
print (timepoint)
print (cpuusage)

timepoint2 = timepoint[0:]
cpuusage2 = cpuusage[0:]

tick_spacing = 40
fig, ax = plt.subplots(1,1)
ax.plot(timepoint2, cpuusage2, 's-', color = 'b', label="Hadoop-6133")
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.set_xlabel("Time")
ax.set_ylabel("CPU Utilization")
ax.legend(loc = "best")
plt.show()

with open('hadoop6133-cpu.csv', 'w', newline='') as csvfile:
	fieldnames = ['time', 'CPU']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()
	for i in range(len(timepoint2)):
		writer.writerow({'time': str(timepoint2[i]), 'CPU': str(cpuusage2[i])})