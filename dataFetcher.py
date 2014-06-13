#!/usr/bin/python -u
import urllib
import urllib2
import json
import datetime
import time
import MySQLdb
import sys
import pprint
from timeout import timeout

def log(string):
	print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +' : '+ string)

@timeout(10)
def getData(serverAdress):
	return urllib2.urlopen(serverAdress).read()

serverAdress = "http://192.168.2.68/"

while(True):
	# Database connection
	db = MySQLdb.connect(host="localhost", user="oasis", passwd="oasis", db="oasis") 				  
	cur = db.cursor() 
	 
	# Fetching data from arduino
	jsonContent = False
	try:
		log('Contacting server at '+serverAdress)
		jsonContent = getData(serverAdress)
	except:
		log('ERROR: Server is unreachable')
		time.sleep(15)

 
	if(jsonContent):
		try:
			measures = json.loads(jsonContent)   
			currentDate = datetime.datetime.now()  
			goodReading = True
			log('Measures: '+str(measures))

			#Checking the data 
			for p in measures.keys():
				if( p!='date' and ((measures[p] > 84) or (measures[p] < -20))):
					goodReading=False
		except:
			log('ERROR: Parsing exception')
			goodReading = False

		if(goodReading):
			# Inserting data into the database
			try:
				postUrl = 'http://192.168.2.42:8000/backend/records'
				for m in measures.keys():
					values = {'address' : m,
					          'date' : currentDate,
					          'measure' : measures[m] }

					data = urllib.urlencode(values)
					req = urllib2.Request(postUrl, data)
					response = urllib2.urlopen(req)
					
			except:
				log("ERROR: Problem inserting in the database")		

			time.sleep(15)				


