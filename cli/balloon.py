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
import pickle

# This will insert the parent directory to the path so we can import
# the settings.
sys.path.insert(0, os.path.normpath(sys.path[0]+"/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from szp.models import Contest, Submission, Result

from subprocess import Popen, PIPE, STDOUT

f = open (sys.path[0]+"/cli/template_ballon.ps")
postscript_template = f.read()
f.close()

try:
	f = open(sys.path[0]+"/cli/balloon-pickle")
	balloons = pickle.load(f)
	f.close()
	print "Some pickled balloons found."
except IOError:
	balloons = {}
	print "No pickled balloons found."

while True:
	contest = Contest.objects.get()

	if contest.status != "RUNNING":
		print "\n\nContest is not running, exiting."
		sys.exit(1)

	submissions = Submission.objects.filter(result__judgement__exact="ACCEPTED", team__teamclass__rank__gt=0)
	
	for b in submissions:
		t = b.team_id
		p = b.problem_id
		
		if t not in balloons:
			balloons[t] = []
			
		if p not in balloons[t]:
			print "\nBalloon for team '%s' (%s), problem %s, colour %s" % (b.team.name, b.team.location, str(b.problem.letter), b.problem.colour)
			
			teamname = b.team.name
			teamname = teamname[:39] + '...' if len(teamname) > 42 else teamname
			
			postscript = postscript_template
			postscript = postscript.replace("TEAM", teamname).replace("LOCATION", b.team.location)\
									.replace("PROBLEM", str(b.problem)).replace("COLOUR", b.problem.colour)
			postscript = postscript.encode("utf-8")
			f = open("/tmp/balloon.ps", "w+")
			f.write(postscript)
			f.seek(0)
			ret = Popen(["/usr/bin/lpr","-o","job-sheets=none","-P","szpprinter"], stdin=f, close_fds=True)
			f.close()
			
			balloons[t].append(p)
			
			f = open(sys.path[0]+"/cli/balloon-pickle", "w")
			pickle.dump(balloons, f)
			f.close()

	sys.stdout.write('.')
	sys.stdout.flush()
	time.sleep(5)
