#!/usr/bin/python
import urllib2
import json
import datetime
import MySQLdb

# Database connection
db = MySQLdb.connect(host="localhost", user="root", passwd="", db="thermometers") 				  
cur = db.cursor() 
   
# Fetching data from arduino
jsonContent = urllib2.urlopen("http://192.168.2.77:88/").read()
temperatures = json.loads(jsonContent)   
temperatures["date"] = datetime.datetime.now()  

# Inserting data into the database
try:
   cur.execute("INSERT INTO temperature_sensors(date, thermometer_1, thermometer_2, thermometer_3, thermometer_4, thermometer_5) VALUES (%s,%s,%s,%s,%s,%s)",(temperatures["date"].strftime('%Y-%m-%d %H:%M:%S'),float(temperatures["0"]),float(temperatures["1"]),float(temperatures["2"]),float(temperatures["3"]),float(temperatures["4"])))
   db.commit()
except:
   db.rollback()
  
db.close()					

