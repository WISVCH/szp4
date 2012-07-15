#!/usr/bin/python

import os
import sys
import shutil

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0] + "/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from szp.models import File

dir = os.path.join(os.getcwd(), "szp-files")
if os.path.exists(dir):
    shutil.rmtree(dir)
os.mkdir(dir)

for file in File.objects.all():
    print "Exporting file %d" % file.id

    file_name = os.path.join(dir, str(file.id))
    fp = open(file_name, "w")
    fp.write(file.content.encode("utf-8"))
    fp.close()
