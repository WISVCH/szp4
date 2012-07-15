#!/usr/bin/python

import MySQLdb

conn = MySQLdb.connect(host="localhost",
                        user="chipcie",
                        passwd="",
                        db="chipcie")
cursor = conn.cursor()
cursor.execute("SELECT * from inschr2010")
i = 0
for row in cursor:
    i += 1
    print "szp addteam -ip team%02d '%s' 'TU Delft' %d 'DW 150.01'" % (i, row[0], row[18] + 1)
