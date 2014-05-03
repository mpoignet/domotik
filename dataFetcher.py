#!/usr/bin/python -u
import urllib2
import json
import datetime
import time
import MySQLdb
import sys
import pprint

def log(string):
	print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +' : '+ string)

serverAdress = "http://192.168.2.79/"

while(True):
	# Database connection
	db = MySQLdb.connect(host="localhost", user="oasis", passwd="oasis", db="oasis") 				  
	cur = db.cursor() 
	 
	# Fetching data from arduino
	jsonContent = False
	try:
		log('Contacting server at '+serverAdress)
		jsonContent = urllib2.urlopen(serverAdress).read()
	except:
		log('ERROR: Server is unreachable')
		time.sleep(15)

	if(jsonContent):
		measures = json.loads(jsonContent)   
		measures["date"] = datetime.datetime.now()  
		goodReading = True;
		log('Measures: '+str(measures))

		#Checking the data 
		for p in measures.keys():
			if(measures[p]==85):
				goodReading=False

		if(goodReading):
			#Converting data types to please the db
			measures["date"] = measures["date"].strftime('%Y-%m-%d %H:%M:%S')

			# Inserting data into the database
			try:
			    cur.execute("INSERT INTO data(date, t0, t1, t2, t3, t4, c0) VALUES (%s,%s,%s,%s,%s,%s,%s)",(measures["date"],measures["0"],measures["1"],measures["2"],measures["3"],measures["4"],measures["c"]))
			    db.commit()
			except MySQLdb.Error, e:
			    log("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
			    db.rollback()
			  
			db.close()	
			time.sleep(15)				


