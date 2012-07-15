#!/usr/bin/python

import os
import sys

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0] + "/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from szp.models import Submission

for submission in Submission.objects.all():
    print "Rejudging submission %s for problem %s." % (submission.id, submission.problem.letter)
    submission.autojudge = None
    submission.result = None
    submission.status = "NEW"
    submission.save()
