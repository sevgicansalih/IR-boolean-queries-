from stemmer import PorterStemmer
import string
import re
import pickle
import copy
import os.path
from os import listdir

directory = 'Dataset/'

list = [] # holds every document by their index (i)

def main():
	if not (os.path.exists('stemmedDictList.pickle') and os.path.exists('stemmedNormalList.pickle') and os.path.exists('positionalIndex.pickle')):

		rex = re.compile(r'<REUTERS.*?>(.*?)</REUTERS>.*?',re.DOTALL)

		news = []


		onlyfiles = [f for f in listdir('Dataset') if os.path.isfile(os.path.join('Dataset', f))]
		print sorted(onlyfiles)

		for file in sorted(onlyfiles):
			if file.endswith('.sgm'):
				dir = directory+file
				f = open(dir,'r')
				data = f.read()
			
				#Find reuter tags (new id) in a single sgm file
				reutersMatch = rex.findall(data)
				for j in range(len(reutersMatch)):
					titleMatch = getTitleMatch(reutersMatch[j])
					bodyMatch = getBodyMatch(reutersMatch[j])
					
					if len(titleMatch)==1 and len(bodyMatch)==1:
						news.append(titleMatch[0] + " " + bodyMatch[0])
					elif len(titleMatch)==1 and len(bodyMatch)==0:
						news.append(titleMatch[0])
					elif len(titleMatch)==0 and len(bodyMatch)==1:
						news.append(bodyMatch[0])
					else:
						news.append(' ')

				f.close()
		"""
		i=0
		while i != 22:
			if i<10:
				dir = directory + '00{}.sgm'.format(i)
			else:
				dir = directory + '0{}.sgm'.format(i)

			f = open(dir,'r')
			data = f.read()
			print 'Reading file : ',i
			i = i+1
			
			#Find reuter tags (new id) in a single sgm file
			reutersMatch = rex.findall(data)
			for j in range(len(reutersMatch)):
				titleMatch = getTitleMatch(reutersMatch[j])
				bodyMatch = getBodyMatch(reutersMatch[j])
				
				if len(titleMatch)==1 and len(bodyMatch)==1:
					news.append(titleMatch[0] + " " + bodyMatch[0])
				elif len(titleMatch)==1 and len(bodyMatch)==0:
					news.append(titleMatch[0])
				elif len(titleMatch)==0 and len(bodyMatch)==1:
					news.append(bodyMatch[0])
				else:
					news.append(' ')

			f.close()
		"""
		# now we have parsed data according to their newid-1 for their index


		# does case folding and normalizations
		caseFolding(news)
		print 'Case Folding DONE'
		removePuncs(news)
		print 'Removing punctiations DONE'

		newsTokens = tokenize(news)

		print 'Tokenizing DONE'

		dictList,normalList = stopwordRemoval(newsTokens)

		print 'Stopword Removal DONE'


	#print dictList[21577] , len(dictList[21577])

	if os.path.exists('stemmedDictList.pickle'):
		# this method gets list from a file 
		stemmedDictList = getDumpedFile('stemmedDictList.pickle')
		print 'Dictionary got from dumped file'

	else:
		# this method calculates list but it takes so long
		stemmedDictList = stemize(dictList)
		dumpFile(stemmedDictList,'stemmedDictList.pickle')
		print 'Dictionary dumped'

	print 'Stemmed as dictionary DONE'

	
	if os.path.exists('stemmedNormalList.pickle'):
		# this method gets list from a file 
		stemmedNormalList = getDumpedFile('stemmedNormalList.pickle')
		print 'stemmedNormalList got from dumped file'

	else:
		# this method calculates list but it takes so long
		stemmedNormalList = stemizeList(normalList)
		dumpFile(stemmedNormalList,'stemmedNormalList.pickle')
		print 'stemmedNormalList dumped'

	print 'Stemmed as list DONE'
	

	if os.path.exists('positionalIndex.pickle'):
		# this method gets list from a file 
		posIndex = getDumpedFile('positionalIndex.pickle')
		print 'posIndex got from dumped file'

	else:
		# this method calculates list but it takes so long
		posIndex = positionalIndexer(stemmedDictList,stemmedNormalList)
		dumpFile(posIndex,'positionalIndex.pickle')
		print 'posIndex Dumped'
	print 'Positional Indexing DONE'

	queryProcessor(stemmedDictList,stemmedNormalList,posIndex)


def queryProcessor(stemmedDictList,stemmedNormalList,posIndex):
	while True:
		filename = raw_input('Enter query : ')
		queryTokens = filename.split()
		caseFolding(queryTokens)
		removePuncs(queryTokens)
		query = stemizeQuery(queryTokens)
		print query
		queryType = query[0]
		if queryType == '1':
			booleanQueryProcessor(query,posIndex)
		elif queryType == '2':
			proximityQueryProcessor(query,posIndex,2)
		elif queryType == '3':
			proximityQueryProcessor(query,posIndex,3)

def proximityQueryProcessor(query,posIndex,type):
	terms = []
	proximity = []
	for index,token in enumerate(query):
		if index == 0 :
			continue
		else:
			if type == 2:
				terms.append(token)
				proximity.append(0)
			elif type == 3:
				if index%2 ==1:
					terms.append(token)
				else:
					proximity.append(int(token[1]))
	if type==2:
		del proximity[-1]
	result = []
	termIndexes = []
	for term in terms:
		termIndexes.append(posIndex[term].keys())
	docIDset = intersect(termIndexes)
	docIDList = sorted(docIDset)
	# now we know the docID's in which all terms are existed.
	checkPositions(docIDList, terms, proximity,posIndex)

def checkPositions(docIDList,terms,proximity,posIndex):
	legth = len(terms)
	result = []
	for index, docID in enumerate(docIDList):
		resultPosition = []
		tempPosition = []
		for indexTerm, term in enumerate(terms):	
			if indexTerm == 0:
				continue
			else:
				if indexTerm == 1:
					#print 'gelmesi gereken list'
					#print posIndex[terms[indexTerm-1]][docID]
					for pos1 in posIndex[terms[indexTerm-1]][docID]:
						for pos2 in posIndex[term][docID]:
							#print 'type pos1: ',type(pos1),'type pos2: ',type(pos2),'pos1: ',pos1, 'pos2: ',pos2,'fark : ', abs(pos1-pos2) , 'proximity ise ', proximity[indexTerm-1]+1
							if pos2-pos1>0 and pos2-pos1<= proximity[indexTerm-1]+1:
								resultPosition.append(pos2)
								#print 'result position : ',len(resultPosition)
				
				
				else:
					#print 'index term 1den farkli'
					tempPosition = copy.deepcopy(resultPosition)
					del resultPosition[:]
					for idxPos,pos3 in enumerate(tempPosition):
						for pos4 in posIndex[terms[indexTerm]][docID]:
							if pos4-pos3 >0 and pos4-pos3 <= proximity[indexTerm-1]+1:
								#print 'girdim buraya'
								resultPosition.append(pos4)
		
		
		if len(resultPosition)!=0:
			result.append(docID)
	print len(result)	
	print result

def booleanQueryProcessor(query,posIndex):
	terms = []
	for index,token in enumerate(query):
		if index == 0:
			continue
		else:
			if index%2 == 1:
				terms.append(token)
	result = []
	termIndexes = []
	for term in terms:
		termIndexes.append(posIndex[term].keys())
	print len(termIndexes)
	result = intersect(termIndexes)
	print sorted(result)

def intersect(termIndexes):
	result = []
	sa = set(termIndexes[0])
	sb = set(termIndexes[1])
	result = sa.intersection(sb)
	for i,termIndex in enumerate(termIndexes):
		if i == 0 or i==1:
			continue
		else:
			sb = set(termIndex)
			result = result.intersection(sb)

	return result



def positionalIntersect(p1,p2,k,posIndex):
	

	"""
	#p1 and p2 are token's dictionary
	temp1 = p1.copy()
	temp2 = p2.copy()
	answer = []
	for docID1, posList1 in temp1:
		for docID2, posList2 in temp2:
			if docID1 == docID2:
				aList = []
				for position1 in posList1:
					for position2 in posList2:
						if abs(position1 - position2) <= k:
							aList.append(position2)
						elif position2 > position1:
							break;

	"""




def dumpFile(data,filename):
	with open(filename, 'wb') as handle:
		pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def getDumpedFile(filename):
	with open(filename, 'rb') as handle:
		data = pickle.load(handle)
		return data
def getStemmedNormalList():
	f = open('stemmedNormalList.txt','r')
	data = f.read()
	
	stemmedNormalList = []
	newIDs = data.split('#')
	for new in newIDs:
		aList = []
		tokens = new.split()
		for token in tokens:
			aList.append(token)
		stemmedNormalList.append(aList)
	return stemmedNormalList
def positionalIndexer(stemmedDictList,stemmedNormalList):
	# a list which holds token id's as index ( all token id's are unique), list member holds a dict, dict key is newID dict value is position in that newID 
	tokenDict = {}

	for indexDoc,aList in enumerate(stemmedNormalList):
		#print 'in another list' , indexDoc
		for indexToken,token in enumerate(aList):
			#print "token ",token," index ", indexToken	
			docIDDict = {}
			positions = []
			if not token in tokenDict:
				positions.append(indexToken)
				docIDDict[indexDoc] = positions
				tokenDict[token] = docIDDict
			else:
				if not indexDoc in tokenDict[token]:
					positions.append(indexToken)
					tokenDict[token][indexDoc] = positions 
				else:
					tokenDict[token][indexDoc].append(indexToken)
			
	"""
	aList = stemmedNormalList[0]
	
	indexDoc = stemmedNormalList.index(aList)
	print 'in another list' , indexDoc
	for indexToken,token in enumerate(aList):

		docIDDict = {}
		positions = []

		print id(positions), " id"
		if not token in tokenDict:
			print "token not in dict"
			positions.append(indexToken)
			docIDDict[indexDoc] = positions
			tokenDict[token] = docIDDict
		else:
			if not indexDoc in tokenDict[token]:
				print "token is in dict but no docDict for this docID"
				positions.append(indexToken)
				tokenDict[token][indexDoc] = positions 
			else:
				print "token is in dict ,position list updated for this docID dict"
				tokenDict[token][indexDoc].append(indexToken)

	print "this is a list"
	print aList
	"""
	#print "this is token dict"
	#print tokenDict	
	
	return tokenDict

def stemize(dictList):
	porter = PorterStemmer()		
	for dict in dictList:
		for token in dict.keys():
			dict[porter.stem(token,0,len(token)-1)] = dict.pop(token)
	return dictList

def stemizeList(normalList):
	porter = PorterStemmer()
	newList = []
	for lists in normalList:
		tokenList = []
		for token in lists:
			#print normalList.index(lists)," ",lists.index(token)
			tokenList.append(porter.stem(token,0,len(token)-1))
		newList.append(tokenList)
			#token = porter.stem(token,0,len(token)-1)
			
	return newList
def stemizeQuery(query):
	porter = PorterStemmer()
	newList = []
	for q in query:
		newList.append(porter.stem(q,0,len(q)-1))
	return newList

def tokenize(news):
	list = []
	for new in news:
		list.append(new.split())
	#print list[0]
	#print list[0][0]
	return list

def stopwordRemoval(newsTokens):
	dictList = []
	normalList = []
	f = open('stopwords.txt','r')
	sList = f.read()
	index = 0
	for i in range(len(newsTokens)):
		aDict = {}
		aList = []
		for r in newsTokens[i]:
			if not r in sList:
				aDict[r] = index
				aList.append(r)
			index = index + 1 

		dictList.append(aDict)
		normalList.append(aList)
	return dictList,normalList

def removePuncs(news):
	for i in range(len(news)):
		news[i] = re.sub(r'[^a-zA-Z0-9]', ' ', news[i]) 

	
def caseFolding(news):
	for i in range(len(news)):
		news[i] = news[i].lower()

def getTitleMatch(data):
	rex = re.compile(r'<TITLE>(.*?)</TITLE>',re.DOTALL)
	titleMatch = rex.findall(data)
	#print "Title length is : ",len(titleMatch)
	#print titleMatch
	return titleMatch


def getBodyMatch(data):
	rex = re.compile(r'<BODY>(.*?)</BODY>',re.DOTALL)
	bodyMatch = rex.findall(data)
	#print "Body length is : ",len(bodyMatch)
	#print bodyMatch
	return bodyMatch

if __name__ == '__main__':
	main();