import matplotlib.pyplot as plt
import csv
import matplotlib.ticker as ticker
import pickle

workstart = 1619203948000 # 14:52:28
workend = 1619204018000 # 14:53:38

start = [1619203949014, 1619203963019, 1619203977035, 1619203991034, 1619204005051]
end = [1619203952253, 1619203966254, 1619203980267, 1619203994295, 1619204008305]
 
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

with open('logseq-17341.pickle', 'wb') as handle:
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
