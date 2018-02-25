from bs4 import BeautifulSoup
import string
import re
directory = 'reuters/reut2-'

list = [] # holds every document by their index (i)

def main():

	"""	
	i=0
	while i != 22:
		if i<10:
			dir = directory + '00{}.sgm'.format(i)
		else:
			dir = directory + '0{}.sgm'.format(i)

		f = open(dir,'r')
		data = f.read()
		soup = BeautifulSoup(data,'html.parser')
		bodys = soup.findAll('body')
		titles = soup.findAll('title')

		print i

		list.append([titles,bodys])
		i = i+1
	"""
	f = open('reuters/reut2-000.sgm','r')
	data = f.read()
	f.close()
	soup = BeautifulSoup(data,'html.parser')
	reuters = soup.findAll('reuters')
	
	print("length of reuters is :")
	print len(reuters)

	for reuter in reuters:
		print reuter['newid']

		# Case folding
		if reuter.title is not None:
			reuter.title.string = reuter.title.string.lower()
			#print reuter.title.string
		if reuter.body is not None:
			reuter.body.string = reuter.body.string.lower()
			#print reuter.body.string

		rawText = reuter.title.string + " " + reuter.body.string
		
		words = rawText.split()


		stripped = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in words]

		for token in stripped:
			print token
	# print 66th news' title from 004.sgm file

	print ('print 66th news\' title from 004.sgm file') 
	#print list[4][0][66]

	print ('print 66th news\' body from 004.sgm file')
	# print 66th news' body from 004.sgm file
	#print list[4][1][66]

if __name__ == '__main__':
	main();