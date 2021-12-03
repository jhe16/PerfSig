import matplotlib.pyplot as plt
import csv
import matplotlib.ticker as ticker
import pickle

workstart = 1621609853000 # 11:10:53
workend = 1621609930000 # 11:12:10

start = [1621609857000, 1621609873000, 1621609889000, 1621609905000, 1621609921000]
end = [1621609859000, 1621609875000, 1621609891000, 1621609907000, 1621609923000]
 
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

with open('logseq-7005.pickle', 'wb') as handle:
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
