from stemmer import PorterStemmer
import string
import re
import pickle
import copy
import os.path
from os import listdir

directory = 'Dataset/'

def main():

	"""
	IF REQUIRED LISTS ARE DUMPED NO NEED TO READ IT FROM FILES AGAIN
	"""

	if not (os.path.exists('stemmedDictList.pickle') and os.path.exists('stemmedNormalList.pickle') and os.path.exists('positionalIndex.pickle')):

		"""
		FIND REUTERS TAGS, ASSUME THAT NEWIDs ARE CONSECUTIVE

		WITH THIS REGEX WE CAN FIND ALL NEWS
		"""

		rex = re.compile(r'<REUTERS.*?>(.*?)</REUTERS>.*?',re.DOTALL)

		news = []

		"""
		READ FILES IN DATASET DIRECTORY
		"""
		onlyfiles = [f for f in listdir('Dataset') if os.path.isfile(os.path.join('Dataset', f))]
		#print sorted(onlyfiles)

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
	
		# now we have parsed data according to their newid-1 for their index

		#TOKENIZER
		tempNewsTokens = tokenize(news)


		# CALCULATES NUMBER OF UNIQUE TOKENS BEFORE PROCESSING
		numOfUniqueTokensBefore = 0
		tempDict = {}
		count = 0
		for new in tempNewsTokens:
			for token in new:
				if  token in tempDict:
					count = tempDict[token]
					tempDict[token] = count+1
				else:
					tempDict[token] = 1
		numOfUniqueTokensBefore = len(tempDict)

		print 'Number of UNIQUE tokens before stopword removal and stemming', numOfUniqueTokensBefore

		i = 0
		print 'Frequency of the dictionary keys before stopword removal'
		for w in sorted(tempDict, key=tempDict.get, reverse=True):
			if i < 20:
				print w, tempDict[w]
			else:
				break
			i = i+1


		# does case folding and normalizations
		caseFolding(news)
		print 'Case Folding DONE'
		removePuncs(news)
		print 'Removing punctiations DONE'



		newsTokens = tokenize(news)
		print 'Tokenizing DONE'
		# CALCULATES UNIQUE TOKEN NUMBER BEFORE NORMALIZATIONS		
		numOfUniqueTokensBefore = 0
		tempDict = {}
		count = 0
	
		for new in newsTokens:
			for token in new:
				tempDict[token] = count
				count = count+1
		numOfUniqueTokensBefore = len(tempDict)

		# CALCULATES TOKEN NUMBER BEFORE NORMALIZATIONS
		numOfTokensBefore = 0
		for new in newsTokens:
			numOfTokensBefore = numOfTokensBefore + len(new)

		print 'Number of tokens before stopword removal and stemming', numOfTokensBefore

		# STOPWORD REMOVAL
		dictList,normalList = stopwordRemoval(newsTokens)

		print 'Stopword Removal DONE'




	"""
	THIS PART DUMPS CALCULATED DATA BY USING PICKLE, IF FILES EXIST, IT IMPORTS THEM
	"""
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
		stemmedNormalList,fuckingRetarded = stemizeList(normalList)
		dumpFile(stemmedNormalList,'stemmedNormalList.pickle')
		print 'stemmedNormalList dumped'
		numOfUniqueTokensAfter = len(fuckingRetarded)
		print 'Number of UNIQUE tokens after stopword removal and stemming', numOfUniqueTokensAfter
		i = 0 
		print 'Frequency of the dictionary keys after stopword removal'
		for w in sorted(fuckingRetarded, key=fuckingRetarded.get, reverse=True):
			if i<20:
				print w, fuckingRetarded[w]
			else:
				break
			i = i+1	

	print 'Stemmed as list DONE'
	
	# CALCULATES NUMBER OF TOKENS AFTER NORMALIZATION
	numOfTokensAfter = 0
	for aList in stemmedNormalList:
		numOfTokensAfter = len(aList) + numOfTokensAfter
	print 'Number of tokens after stopword removal and stemming', numOfTokensAfter


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


	# PASS DATA TO QUERY PROCESSOR
	queryProcessor(stemmedDictList,stemmedNormalList,posIndex)


def queryProcessor(stemmedDictList,stemmedNormalList,posIndex):
	# GETS DATA, WAITS FOR USER INPUT, AND PASSES INFORMATION TO SPECIFIED PROCESSORS
	while True:
		filename = raw_input('Enter query : ')
		queryTokens = filename.split()

		# QUERY NORMALIZATIONS
		caseFolding(queryTokens)
		removePuncs(queryTokens)
		query = stemizeQuery(queryTokens)
		#print query
		queryType = query[0]
		if queryType == '1':
			booleanQueryProcessor(query,posIndex)
		elif queryType == '2':
			proximityQueryProcessor(query,posIndex,2)
		elif queryType == '3':
			proximityQueryProcessor(query,posIndex,3)

def proximityQueryProcessor(query,posIndex,type):
	"""
	TYPE 2 IS FOR PHRASE QUERIES

	TYPE 3 IS FOR PROXIMITY QUERIES

	HOLDS TERMS IN QUERY, AND CREATES A LIST OF PROXIMITY OF TERMS
	IF THIS IS PHRASE QUERY, PROXIMITY LIST WILL BE FILLED WITH ZEROs

	"""

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
	
	"""
	THIS PART DOES NORMAL INTERSECTION PROCESS AS IT IS LIKE IN BOOLEAN QUERY PROCESSOR

	CREATES LIST OF COMMON DOCIDs
	"""
	termIndexes = []
	for term in terms:
		termIndexes.append(posIndex[term].keys())
	docIDset = intersect(termIndexes)
	docIDList = sorted(docIDset)


	# now we know the docID's in which all terms are existed.
	checkPositions(docIDList, terms, proximity,posIndex)

def checkPositions(docIDList,terms,proximity,posIndex):
	"""
	THIS PART ITERATES OVER DOCIDs
	AFTER WE ITERATE OVER QUERY TERMS
	STARTING FROM INDEX# = 1 (NOT ZERO) CONTROLS TERMS POSITIONS UNDER SPECIFIED DOCID TWO BY TWO i.e. term0 and term1, term3 and term4

	IN EVERY ITERATION IF THE NEXT TERM EXISTS IN GIVEN PROXIMITY, IT WILL BE ADDED TO RESULT LIST

	"""
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
	# SINCE MY DOCIDs STARTS FROM ZERO, I ADD ONE
	newResult = []
	for res in result:
		newResult.append(res+1)
	print newResult

def booleanQueryProcessor(query,posIndex):
	"""
	GETS QUERY TERMS, GETS POSITIONAL INDEX, INTERSECTS DOCIDs OF TERMS AND ADDS TO THE RESULT REGARDLESS OF TERM'S POSITION
	"""
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
	#print len(termIndexes)
	result = intersect(termIndexes)
	newResult = []
	for res in sorted(result):
		newResult.append(res+1)
	print newResult

def intersect(termIndexes):
	"""
	BY USING SETS WE CAN FIND COMMON ELEMENTS IN A LIST
	"""
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


def dumpFile(data,filename):
	# PICKLE DUMPING FILE
	with open(filename, 'wb') as handle:
		pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def getDumpedFile(filename):
	# PICKLE LOADING FILE FROM DIRECTORY
	with open(filename, 'rb') as handle:
		data = pickle.load(handle)
		return data
def getStemmedNormalList():
	# A METHOD FOR TESTING NOT REQUIRED FOR PROJECT
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
	"""
	{terms:{docIDs : [positions]}}

	EXACTLY DOES THE THING SHOWN ABOVE

	"""
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
			
	
	return tokenDict

def stemize(dictList):
	#STEMIZER FOR DICTIONARY
	porter = PorterStemmer()		
	for dict in dictList:
		for token in dict.keys():
			dict[porter.stem(token,0,len(token)-1)] = dict.pop(token) 
	return dictList

def stemizeList(normalList):
	# STEMIZER FOR LIST
	porter = PorterStemmer()
	newList = []
	newDict = {}
	count = 0;	
	for lists in normalList:
		tokenList = []
		for token in lists:
			#print normalList.index(lists)," ",lists.index(token)
			tokenList.append(porter.stem(token,0,len(token)-1))
			if token in newDict:
				count = newDict[token]
				newDict[token] = count +1
			else:
				newDict[token] = 1
		newList.append(tokenList)
			#token = porter.stem(token,0,len(token)-1)
			
	return newList,newDict
def stemizeQuery(query):
	# STEMIZER FOR QUERY
	porter = PorterStemmer()
	newList = []
	for q in query:
		newList.append(porter.stem(q,0,len(q)-1))
	return newList

def tokenize(news):
	# TOKENIZER LIST OF NEWS

	list = []
	for new in news:
		list.append(new.split())
	#print list[0]
	#print list[0][0]
	return list

def stopwordRemoval(newsTokens):
	# GETS STOPWORDS FROM STOPWORD FILE, IF EXISTS IT REMOVES THEM
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
	# REMOVING PUNCTIATIONS FROM NEWS LIST
	for i in range(len(news)):
		news[i] = re.sub(r'[^a-zA-Z0-9]', ' ', news[i]) 

	
def caseFolding(news):
	# LOWERS NEWS
	for i in range(len(news)):
		news[i] = news[i].lower()

def getTitleMatch(data):
	# GETS TITLE INSIDE OF REUTERS TAG
	rex = re.compile(r'<TITLE>(.*?)</TITLE>',re.DOTALL)
	titleMatch = rex.findall(data)
	#print "Title length is : ",len(titleMatch)
	#print titleMatch
	return titleMatch


def getBodyMatch(data):
	# GETS BODY TEXT INSIDE OF REUTERS TAG
	rex = re.compile(r'<BODY>(.*?)</BODY>',re.DOTALL)
	bodyMatch = rex.findall(data)
	#print "Body length is : ",len(bodyMatch)
	#print bodyMatch
	return bodyMatch

if __name__ == '__main__':
	main();