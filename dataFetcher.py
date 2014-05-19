#!/usr/bin/python -u
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
	#return urllib2.urlopen(serverAdress).read()
	return '{"28844A68050000C5":23.62,"2843AE680500001A":23.56,"28B377670500005F":23.50}'

serverAdress = "http://192.168.2.79/"

#while(True):
# Database connection
db = MySQLdb.connect(host="localhost", user="oasis", passwd="oasis", db="oasis2") 				  
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
			for m in measures.keys():
				cur.execute("SELECT id FROM temperatures_device WHERE address=%s", (m))
				if(cur.rowcount > 0):
					result = cur.fetchone()
					device_id = int(result[0])
				else:
					cur.execute("INSERT INTO temperatures_device(address) VALUES (%s)", (m))
					device_id = cur.lastrowid

				cur.execute("INSERT INTO temperatures_record(date,measure, device_id) VALUES (%s,%s,%s)", (currentDate.strftime("%Y-%m-%d %H:%M:%S"), measures[m], device_id))
			db.commit()
		except MySQLdb.Error, e:
		    log("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
		    db.rollback()
		except:
			log("ERROR: Problem inserting in the database")
			db.rollback()
		  
		db.close()	
		#time.sleep(15)				


