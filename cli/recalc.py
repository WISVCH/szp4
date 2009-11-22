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

teams = {}
contest = Contest.objects.get()

for s in Submission.objects.order_by('timestamp'):
	try:
		result = s.result_set.get()
	except ObjectDoesNotExist:
		print "%s -- %s " % (s, s.status)
		print "-- No result!"
		continue
	print "%s -- %s " % (s, result.judgement)
	
	if s.team not in teams:
		teams[s.team] = {}
	
	if s.problem not in teams[s.team]:
		teams[s.team][s.problem] = {'count': 1, 'solved': False}
	elif not teams[s.team][s.problem]['solved']:
		teams[s.team][s.problem]['count'] += 1
	else:
		print "-- Was already solved!"
	
	if teams[s.team][s.problem]['solved'] == False and result.judgement == "ACCEPTED":
		teams[s.team][s.problem]['solved'] = True
		teams[s.team][s.problem]['solved_time'] = s.timestamp

print "\n------------------------------ SCORES ------------------------------"

for team in teams:
	print '\n', team
	for problem in teams[team]:
		solved = "V" if teams[team][problem]['solved'] else ' '
		print "\t%s: %d %s" % (problem.letter, teams[team][problem]['count'], solved),
		
		try:
			score = Score.objects.get(team=team, problem=problem)
		except ObjectDoesNotExist:
			score = Score(team=team, problem=problem, submission_count=0, correct=False)
		
		score.correct = False
		score.submission_count = teams[team][problem]['count']
		if teams[team][problem]['solved']:
			score.correct = True
			timedelta = (teams[team][problem]['solved_time'] - contest.starttime)
			score.time = timedelta.days*24 + timedelta.seconds/60
			
		score.save()