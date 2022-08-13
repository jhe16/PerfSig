from string import digits
import numpy as np
from sklearn.cluster import DBSCAN
import editdistance
from sklearn.cluster import AffinityPropagation
import distance
from prefixspan import PrefixSpan
import time
from collections import OrderedDict
from operator import itemgetter 

from gensim.models import Word2Vec

from sklearn_som.som import SOM
  
from sklearn.feature_extraction.text import CountVectorizer

from hdp import gettopics

from dbidf import dbidf

from dbidf import dbemb

from hbaseprocessing import hbaseprocess

from hbaseprocessing import dbvar

def preprocess():
	filepath = "/Users/Jingzhu/Documents/ExtractSignature/logs/hadoop9106/9106-normal.log"
	f = open(filepath, "r")
	lines = f.readlines()
	logentries = []
	timepoint = []
	for line in lines:
		logsplit1 = line.split(": ", 1)   # seperate log entry
		logsplit2 = logsplit1[0].split()    # seperate date, time, info and class name
		if (len(logsplit1) == 2 and len(logsplit2) == 4):
			# print(logsplit2)
			# print(logsplit1[1])
			processline = logsplit2 + [logsplit1[1]]
			# print (processline)
			# logentry = logsplit1[1].translate(None, digits)
			# print logentry
			logentries += [logsplit2[-1] + ': ' + logsplit1[1]]
			# logentries += [logsplit1[1]]
			date_time = '20' + logsplit2[0] + ' ' + logsplit2[1]
			pattern = '%Y/%m/%d %H:%M:%S'
			epoch = int(time.mktime(time.strptime(date_time, pattern)))
			timepoint += [epoch]

	# print (timepoint)

	f = open("preprocess.log", "w")
	for i in range(len(timepoint)):
		f.write(str(timepoint[i]) + ': ' + logentries[i])

	f.close()

	return logentries, timepoint


def getlogpattern(entries):
	entries = np.asarray(entries)
	# print (entries)
	lev_similarity = np.array([[distance.levenshtein(w1,w2) for w1 in entries] for w2 in entries])
	print (lev_similarity)

	dbcluster = DBSCAN(eps=0.1, min_samples=1, metric="precomputed")
	dbcluster.fit(lev_similarity)
	
	return dbcluster.labels_


# get word embedding for each log entry
def sent_vectorizer(sent, model):
    sent_vec =[]
    numw = 0
    for w in sent:
        try:
            if numw == 0:
                sent_vec = model[w]
            else:
                sent_vec = np.add(sent_vec, model[w])
            numw+=1
        except:
            pass
     
    return (np.asarray(sent_vec) / numw).tolist()


def getallembedding(logentries):
	logsentence = []
	for entry in logentries:
		tmp = entry.lower().split()
		proentry = []
		for word in tmp:
			while (len(word) > 0) and (word[-1] == '.' or word[-1] == ':' or word[-1] == ','):
				word = word[:-1]
			proentry.append(word)
		logsentence.append(proentry)

	model = Word2Vec(logsentence, min_count=3)

	X=[]
	for sentence in logsentence:
		if len(sent_vectorizer(sentence, model)) == 0:
			X.append([0 for _ in range(100)])
		else:
			X.append(sent_vectorizer(sentence, model))   

	X = np.array(X)
	print ("========================")
	# print (X)
	print (len(X))
	print (len(X[0]))
	return X

def clustervar(logentries, percentile):
	varsentence = []
	for entry in logentries:
		entry = entry.strip()
		if entry[-1] == '.':
			entry = entry[:-1]
		tmp = []
		for word in entry.split():
			while (len(word) > 0) and (word[-1] == '.' or word[-1] == ':' or word[-1] == ','):
				word = word[:-1]
			if not all(char.isalpha() for char in word):
				tmp.append(word)
		if len(tmp) == 0:
			varsentence.append([''])
		else:
			varsentence.append(tmp)

	print (varsentence)

	matrix = [[0 for _ in range(len(varsentence))] for i in range(len(varsentence))]
	for i in range(len(varsentence)):
		for j in range(len(varsentence)):
			if i != j:
				lev_similarity = np.array([[distance.levenshtein(w1,w2) if min(len(w1), len(w2)) == 0 else float(distance.levenshtein(w1,w2)/min(len(w1), len(w2))) for w1 in varsentence[i]] for w2 in varsentence[j]])
				# lev_similarity = np.array([[float(distance.levenshtein(w1,w2))/float(min(len(w1), len(w2))) for w1 in varsentence[i]] for w2 in varsentence[j]])
				numpar = int(min(len(varsentence[i]), len(varsentence[j])) * percentile / 100)
				if numpar == 0:
					numpar = 1
				dist1 = np.array([min(l) for l in lev_similarity])
				dist2 = np.array([min(l) for l in lev_similarity.transpose()])
				dist1 = np.sort(dist1)
				dist2 = np.sort(dist2)
				tarpar = np.array(dist1[:numpar] + dist2[:numpar])
				matrix[i][j] = np.average(tarpar)

	dbcluster = DBSCAN(eps=1, min_samples=3, metric="precomputed")
	dbcluster.fit(np.array(matrix))
	
	labels = dbcluster.labels_

	clusterid = {}
	for i in range(len(labels)):
		if labels[i] not in clusterid:
			clusterid[labels[i]] = [i]
		else:
			clusterid[labels[i]].append(i)

	for id in clusterid:
		print (str(id) + ': ')
		for i in clusterid[id]:
			print (logentries[i])

	return labels
	

def clusteridf(logentries):
	# wordmap = {}
	# for line in logentries:
	# 	words = line.strip().split()
	# 	for w in words:
	# 		if w in wordmap:
	# 			wordmap[w] += 1
	# 		else:
	# 			wordmap[w] = 1

	# numword = 3
	# varvec = []
	# corpus = []
	# for line in logentries:
	# 	print (line)
	# 	words = line.strip().split()
	# 	tmp = {}
	# 	for w in words:
	# 		tmp[w] = wordmap[w]
	# 	tmp = sorted(tmp.items(), key = lambda kv:kv[1])
	# 	vec = []
	# 	doc = ''
	# 	for i in range(min(numword,len(words))):
	# 		vec.append(tmp[i][0])
	# 		print (tmp[i])
	# 		doc += tmp[i][0] + ' '

	# 	while len(vec) < numword:
	# 		vec.append('')

	# 	varvec.append(vec)

	# 	corpus.append(doc)

	corpus = []
	for line in logentries:
		corpus.append(line)

	vectorizer = CountVectorizer()
	X = vectorizer.fit_transform(corpus)
	tf = X.toarray()
	print (tf)

	som = SOM(m=5, n=5, dim=len(tf[0]))
	labels = som.fit_predict(tf)
	print (labels)
	print (len(labels))



	# matrix = [[0 for _ in range(len(varvec))] for i in range(len(varvec))]
	# for i in range(len(varvec)):
	# 	for j in range(len(varvec)):
	# 		if i != j:
	# 			lev_similarity = np.array([[distance.levenshtein(w1,w2) for w1 in varvec[i]] for w2 in varvec[j]])
	# 			dist1 = np.array([min(l) for l in lev_similarity])
	# 			dist2 = np.array([min(l) for l in lev_similarity.transpose()])
	# 			dist1 = np.sort(dist1)
	# 			dist2 = np.sort(dist2)
	# 			tarpar = np.array(dist1 + dist2)
	# 			matrix[i][j] = np.average(tarpar)

	# dbcluster = DBSCAN(eps=0.5, min_samples=5, metric="precomputed")
	# dbcluster.fit(np.array(matrix))
	
	# labels = dbcluster.labels_

	clusterid = {}
	for i in range(len(labels)):
		if labels[i] not in clusterid:
			clusterid[labels[i]] = [i]
		else:
			clusterid[labels[i]].append(i)

	for id in clusterid:
		print (str(id) + ': ')
		for i in clusterid[id]:
			print (logentries[i])

	return labels



def splitonworkload(wordemb, logentries):
	som = SOM(m=5, n=5, dim=100)
	labels = som.fit_predict(wordemb)
	print (labels)
	print (len(labels))

	clusterid = {}
	for i in range(len(labels)):
		if labels[i] not in clusterid:
			clusterid[labels[i]] = [i]
		else:
			clusterid[labels[i]].append(i)

	for id in clusterid:
		print (str(id) + ': ')
		for i in clusterid[id]:
			print (logentries[i])

	return labels
	



def getsamelog(logentries):
	entries = []
	for entry in logentries:
		tmp = ''
		words = entry.split()
		# print (words)
		# print (tmp)
		for word in words:
			while (len(word) > 0) and (word[-1] == '.' or word[-1] == ':' or word[-1] == ','):
				word = word[:-1]
			if not all(char.isalpha() for char in word):
				tmp += '* '
			else:
				tmp += word + ' '
		entries += [tmp[:-1]]
		# print (tmp)

	# clusterlabel = getlogpattern(entries)

	clusterid = {}
	for i in range(len(entries)):
		if entries[i] not in clusterid:
			clusterid[entries[i]] = [i]
		else:
			clusterid[entries[i]].append(i)

	clusterlabel = [0 for _ in range(len(entries))]
	idx = 0
	for id in clusterid:
		idx += 1
		for i in clusterid[id]:
			clusterlabel[i] = idx

	print ('log pattern extraction: ')
	idx = 0
	for id in clusterid:
		idx += 1
		print (str(idx) + ': ')
		print (str(id))
		for i in clusterid[id]:
			print (logentries[i])

	return clusterlabel, entries


def calthreshold(totaltimegap):
	alpha = 1
	totaltimegap = np.array(totaltimegap)
	# print (totaltimegap)
	threshold = np.mean(totaltimegap) + alpha * np.std(totaltimegap)
	# print (threshold)
	return threshold


def getpruneset(labels):
	candlogidx = {}   # build dict based on label
	for i in range(len(labels)):
		if labels[i] not in candlogidx:
			candlogidx[labels[i]] = [i]
		else:
			candlogidx[labels[i]].append(i)

	freqthres = 3

	pruneset = []      # choose log entries with frequency over 3
	for l in candlogidx:
		if len(candlogidx[l]) >= freqthres:
			pruneset += candlogidx[l]

	pruneset.sort()
	return pruneset, candlogidx


def grouponfreq(candlogidx):
	labeltolog = []
	freq = []
	freqthres = 3
	for l in candlogidx:
		if len(candlogidx[l]) >= freqthres:
			labeltolog.append(candlogidx[l])
			freq.append(len(candlogidx[l]))

	print ('label: ')
	print (labeltolog)
	print ('freq: ')
	print (freq)

	freqdistance = np.array([[abs(f1 - f2) for f1 in freq] for f2 in freq])
	dbcluster = DBSCAN(eps=0.1, min_samples=3, metric="precomputed")
	dbcluster.fit(freqdistance)
	clusterid = {}
	for i in range(len(dbcluster.labels_)):
		if dbcluster.labels_[i] not in clusterid:
			clusterid[dbcluster.labels_[i]] = [i]
		else:
			clusterid[dbcluster.labels_[i]].append(i)


	splitlog = []
	for i in clusterid:
		tmp = []
		for j in clusterid[i]:
			tmp += labeltolog[j]
		tmp.sort()
		splitlog.append(tmp)

	print (splitlog)
	return splitlog


def splitoncluster(clusterlabel):
	splitlog = []
	clusterid = {}
	for i in range(len(clusterlabel)):
		if clusterlabel[i] not in clusterid:
			clusterid[clusterlabel[i]] = [i]
		else:
			clusterid[clusterlabel[i]].append(i)

	for id in clusterid:
		splitlog.append(clusterid[id])

	return splitlog



def getlogandgap(timepoint, pruneset):
	prev = 0
	next = 0
	totaltimegap = []
	for i in pruneset:
		next = timepoint[i]
		if prev != 0:
			totaltimegap.append(next - prev)
		prev = next

	return totaltimegap

def splitloggroup(pruneset, totaltimegap, threshold):
	splitlogset = [[pruneset[0]]]
	group = 0
	for i in range(len(totaltimegap)):
		if totaltimegap[i] > threshold:
			splitlogset.append([])
			group += 1
			splitlogset[group].append(pruneset[i+1])
		else:
			splitlogset[group].append(pruneset[i+1])

	# print (splitlogset)
	return splitlogset



def frequentPattern(logtemplate, timepoint, clusterlabel):
	# logtemplate = logtemplate.tolist()
	print (logtemplate)

	# pruneset, candlogidx = getpruneset(logtemplate)

	# print (pruneset)

	# # group based on frequency

	# grouplog = grouponfreq(candlogidx)

	grouplog = splitoncluster(clusterlabel)

	# seperate based on time gap

	finalsplitlog = []

	for subset in grouplog: 

		if len(subset) <= 2:
			finalsplitlog += [subset]
			continue

		else:

			totaltimegap = getlogandgap(timepoint, subset)

			print ('timegap: ')
			print (totaltimegap)

			threshold = calthreshold(totaltimegap)

			print ('threshold is: ' + str(threshold))

			splitlogset = splitloggroup(subset, totaltimegap, threshold) 

			finalsplitlog += splitlogset




	print ('final split log is: ')
	print (finalsplitlog)

	seqinp = []
	for logsubset in finalsplitlog:
		tmp = []
		for i in logsubset:
			tmp.append(logtemplate[i])
		seqinp.append(tmp)

	print ('sequence mining input is: ')
	print (seqinp)


	ps = PrefixSpan(seqinp)
	print (ps.topk(10, closed=True))


if __name__ == "__main__":
	logentries, timepoint = preprocess()

	# logentries, timepoint = hbaseprocess()

	logtemplate, entries = getsamelog(logentries)

	# labels = dbvar(logentries, 50)

	# labels = clustervar(logentries, 50)

	# labels = clusteridf(logentries)

	# labels = dbidf(logentries)

	# labels = gettopics(logentries)

	wordemb = getallembedding(logentries)

	labels = splitonworkload(wordemb, logentries)

	# labels = dbemb(wordemb, logentries)

	frequentPattern(logtemplate, timepoint, labels)
	

