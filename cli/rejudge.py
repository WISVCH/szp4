#!/usr/bin/python

import os
import sys

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0]+"/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Permission
from szp.models import *

number = sys.argv[1]

submission = Submission.objects.get(id=number)
submission.autojudge = None

try:
	submission.result.delete()
except:
	print 'No result object.'

submission.status = "NEW"
submission.save()

print "Rejudging submission %s for problem %s." % (number, submission.problem.letter)