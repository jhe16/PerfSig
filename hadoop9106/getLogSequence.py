import matplotlib.pyplot as plt
import csv
import matplotlib.ticker as ticker
import pickle

workstart = 1617984807000 # 12:13:27
workend = 1617984860000 # 12:14:20

start = [1617984807000, 1617984819000, 1617984832000, 1617984844000, 1617984856000]
end = [1617984809000, 1617984821000, 1617984833000, 1617984845000, 1617984857000]
 
interval = 1000 # sampling interval

timevector = [0 for _ in range(int((workend - workstart) / interval))]
print (timevector)
print (len(timevector))

for i in range(len(start)):
    time = start[i]
    while time < end[i]:
        idx = int((time - workstart) / interval)
        timevector[idx] = min((idx + 1) * interval + workstart, end[i]) - time 
        time = (idx + 1) * interval + workstart

print (timevector)

with open('logseq-9106.pickle', 'wb') as handle:
    pickle.dump(timevector, handle, protocol=pickle.HIGHEST_PROTOCOL)

x_values=list(range(workstart, workend, interval))

# tick_spacing = 40
fig, ax = plt.subplots(1,1)
ax.plot(x_values, timevector, 's-', color = 'b')
# ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.set_xlabel("Timestamp", fontsize=30)
ax.set_ylabel("Log sequence's total execetion time", fontsize=30)
ax.legend(loc = "best")
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.show()
