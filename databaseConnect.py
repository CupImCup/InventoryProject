#!/usr/bin/python

import MySQLdb

dbconnect = MySQLdb.connect("localhost", "pythonuser", "pythonpwd123", "pythondb")

cursor = dbconnect.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
#check connection, if connection is valid, should print:  Version retrieved:  ('10.5.7-MariaDB',)
if data:
  print('Version retrieved: ', data)
else:
  print('Version not retrieved.')

dbconnect.close()