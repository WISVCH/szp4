#!/usr/bin/python

import os
import sys
import shutil

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0]+"/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from szp.models import *
from django.db import connection, transaction

dir = os.path.join(os.getcwd(),"szp-files")
max_file_id = 0

for file in os.listdir(dir):
	print "Importing file %s" % file
	
	file_name = os.path.join(dir, file)
	fp = open(file_name, "r")
	file_contents = fp.read()
	fp.close()
	
	file_id = int(file)
	max_file_id = file_id if file_id > max_file_id else max_file_id
	
	db_file = File(id=file_id, content=file_contents)
	db_file.save()

cursor = connection.cursor()
cursor.execute("ALTER SEQUENCE public.szp_file_id_seq RESTART WITH %s", [max_file_id+1])
transaction.commit_unless_managed()