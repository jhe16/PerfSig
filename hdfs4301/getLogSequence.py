import matplotlib.pyplot as plt
import csv
import matplotlib.ticker as ticker
import pickle

workstart = 1618537281000 # 21:41:21
workend = 1618537361000 # 21:42:41

start = [1618537281000, 1618537297000, 1618537314000, 1618537330000, 1618537346000]
end = [1618537287000, 1618537303000, 1618537319000, 1618537336000, 1618537352000]
 
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

with open('logseq-4301.pickle', 'wb') as handle:
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
