import stemmer
import string
import re

directory = 'reuters/reut2-'

list = [] # holds every document by their index (i)

def main():
	
	rex = re.compile(r'<REUTERS.*?>(.*?)</REUTERS>.*?',re.DOTALL)

	news = []
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
	
	# now we have parsed data according to their newid-1 for their index

	
	# does case folding and normalizations
	caseFolding(news)
	removePuncs(news)
	newsTokens = tokenize(news)


	dictList = stopwordRemoval(newsTokens)
	#print news[42]
	#print newsTokens[42]
	
	for token in dictList[21577]:
		token = token.stem(token,0,len(token))

	print dictList[21577]


def tokenize(news):
	list = []
	for new in news:
		list.append(new.split())
	#print list[0]
	#print list[0][0]
	return list

def stopwordRemoval(newsTokens):
	dictList = []
	
	f = open('stopwords.txt','r')
	sList = f.read()
	for i in range(len(newsTokens)):
		aDict = {}
		index = 0
		for r in newsTokens[i]:
			if not r in sList:
				aDict[r] = index
			index = index + 1 
		dictList.append(aDict)

	return dictList

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