#!/usr/bin/python

import os
import sys
import time

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0]+"/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from szp.models import Score, Contest

from subprocess import Popen, PIPE, STDOUT

f = open (sys.path[0]+"/cli/template_ballon.ps")
postscript_template = f.read()
f.close()

print "Balloon running"

while True:
    contest = Contest.objects.get()

    if contest.status != "RUNNING":
        sys.exit(1)

    balloons = Score.objects.filter(correct=True).filter(balloon=False)
        
    if not balloons:
		sys.stdout.write('.')
		sys.stdout.flush()
		time.sleep(5)
    else:

        for b in balloons:
            postscript = postscript_template
            postscript = postscript.replace("TEAM", b.team.name[:20]).replace("LOCATION", b.team.location).replace("PROBLEM", str(b.problem)).replace("COLOUR", b.problem.colour)
            postscript = postscript.encode("utf-8")
            f = open("/tmp/balloon.ps", "w+")
            f.write(postscript)
            f.seek(0)
            print "\nBalloon team: %s location: %s problem: %s colour: %s" % (b.team.name, b.team.location, str(b.problem), b.problem.colour)
            ret = Popen(["/usr/bin/lpr","-o","job-sheets=none","-P","szpprinter"], stdin=f, close_fds=True)
            f.close()
            b.balloon = True
            b.save()
