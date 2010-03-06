#!/usr/bin/python
# balloon.py
# Copyright (C) 2008-2009 Jeroen Dekkers <jeroen@dekkers.cx>
# Copyright (C) 2008-2010 Mark Janssen <mark@ch.tudelft.nl>
#
# This file is part of SZP.
# 
# SZP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# SZP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with SZP.  If not, see <http://www.gnu.org/licenses/>.

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

		# FIXME: the Score-model is gone.
		balloons = Score.objects.filter(correct=True).filter(balloon=False)

		if not balloons:
			sys.stdout.write('.')
			sys.stdout.flush()
			time.sleep(5)
		else:

			for b in balloons:
				postscript = postscript_template
				postscript = postscript.replace("TEAM", b.team.name[:25]).replace("LOCATION", b.team.location).replace("PROBLEM", str(b.problem)).replace("COLOUR", b.problem.colour)
				postscript = postscript.encode("utf-8")
				f = open("/tmp/balloon.ps", "w+")
				f.write(postscript)
				f.seek(0)
				print "\nBalloon team: %s location: %s problem: %s colour: %s" % (b.team.name, b.team.location, str(b.problem), b.problem.colour)
				ret = Popen(["/usr/bin/lpr","-o","job-sheets=none","-P","szpprinter"], stdin=f, close_fds=True)
				f.close()
				b.balloon = True
				b.save()
