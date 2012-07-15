#!/usr/bin/python

import os
import sys

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0] + "/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from szp.models import Clarreq, Sentclar

clarreqs = Clarreq.objects.order_by("timestamp")

print "Clarification requests received:"
print
print

for c in clarreqs:
    print "Clarification request from team %s at %s" % (c.sender, c.timestamp)
    print "Subject: %s" % c.subject
    print "Problem: %s" % c.problem
    print
    print c.message
    print

print "Clarifications sent:"
print
print

clars = Sentclar.objects.order_by("timestamp")

for c in clars:
    print "Clarification sent to %s at %s" % (c.receiver, c.timestamp)
    print "Subject: %s" % c.subject
    print "Problem: %s" % c.problem
    print
    print c.message
    print
