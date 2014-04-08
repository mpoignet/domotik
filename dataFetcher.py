#!/usr/bin/python
import urllib2
import json
import datetime
import MySQLdb

# Database connection
db = MySQLdb.connect(host="localhost", user="oasis", passwd="oasis", db="oasis") 				  
cur = db.cursor() 
   
# Fetching data from arduino
jsonContent = urllib2.urlopen("http://192.168.2.77:88/").read()
measures = json.loads(jsonContent)   
measures["date"] = datetime.datetime.now()  

#Converting data types to please the db
measures["date"] = measures["date"].strftime('%Y-%m-%d %H:%M:%S')
measures["0"] = float(measures["0"])
measures["1"] = float(measures["0"])
measures["2"] = float(measures["0"])
measures["3"] = float(measures["0"])
measures["4"] = float(measures["0"])
measures["5"] = float(measures["0"])

# Inserting data into the database
try:
   cur.execute("INSERT INTO data(date, t0, t1, t2, t3, t4, c0) VALUES (%s,%s,%s,%s,%s,%s)",(measures["date"],measures["0"],measures["1"],measures["2"],measures["3"],measures["4"]))
   db.commit()
except:
   db.rollback()
  
db.close()					
