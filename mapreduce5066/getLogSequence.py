import matplotlib.pyplot as plt
import csv
import matplotlib.ticker as ticker
import pickle

workstart = 1617981243000 # 11:14:03
workend = 1617981299000 # 11:14:59

start = [1617981243000, 1617981254000, 1617981265000, 1617981276000, 1617981288000]
end = [1617981244000, 1617981255000, 1617981266000, 1617981277000, 1617981289000]
 
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

with open('logseq-5066.pickle', 'wb') as handle:
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
