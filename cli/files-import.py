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

dir = os.path.join(os.getcwd(),"szp-files")

for file in os.listdir(dir):
	print "Importing file %s" % file
	
	file_name = os.path.join(dir, file)
	fp = open(file_name, "r")
	file_contents = fp.read()
	fp.close()
	
	db_file = File(id=int(file), content=file_contents)
	db_file.save()