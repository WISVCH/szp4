# general.py
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

from szp.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.utils.hashcompat import md5_constructor

def index(request):
	return render_to_response('index.html')

def create_cache_key(name, is_judge=False):
	contest = Contest.objects.get()
	if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
		cache_key = name + '-' + ('jury-' if is_judge else 'team-') + md5_constructor(str(contest.resulttime)).hexdigest()
	else:
		cache_key = name + '-NOINFO'

def check_judge(user):
	profile = user.get_profile()
	return profile.is_judge

def get_scoreboard(is_judge=False):
	contest = Contest.objects.get()
	
	teams = {}
	ranks = {}
	problems = Problem.objects.order_by("letter")

	# Django makes this a LEFT OUTER JOIN, while it could just be a INNER JOIN.
	if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
		submissions = Submission.objects.filter(result__isnull=False)\
			.select_related('result').order_by('result__timestamp')
	else:
		submissions = Submission.objects.filter(result__isnull=False, timestamp__lt=contest.freezetime)\
			.select_related('result').order_by('result__timestamp')

	for submission in submissions:
		t = submission.team_id
		p = submission.problem_id
		
		if t not in teams:
			teams[t] = {}
	
		if p not in teams[t]:
			teams[t][p] = {'count': 1, 'solved': False}
		elif not teams[t][p]['solved']:
			teams[t][p]['count'] += 1
		# else: # Caution: results in extra queries to fetch teamname
			# print "Already solved: %d \t %s" % (result.id, result)

		if teams[t][p]['solved'] == False and submission.result.judgement == "ACCEPTED":
			teams[t][p]['solved'] = True
			teams[t][p]['solved_time'] = submission.timestamp

	if is_judge:
		teamclasses = Teamclass.objects.order_by("rank")
	else:
		teamclasses = Teamclass.objects.filter(rank__gt=0).order_by("rank")

	scoreboard = []
	for teamclass in teamclasses:
		scorelist = []

		for team in Team.objects.filter(teamclass=teamclass).order_by("name"):
			t = team.id
			row = {"id": team.id, "name": team.name, "organisation": team.organisation, "score": 0, "time": 0, "details": []}
			for problem in problems:
				p = problem.id
				try:
					score_dict = {'correct': teams[t][p]['solved'], 'count': teams[t][p]['count']}
					if teams[t][p]['solved']:
						timedelta = (teams[t][p]['solved_time'] - contest.starttime)
						score_dict["time"] = timedelta.days*24 + timedelta.seconds/60
						row["time"] += (teams[t][p]['count'] - 1)*settings.SUBMITFAIL_PENALTY + score_dict["time"]
						row["score"] += 1
				except KeyError:
					score_dict = {'correct': False, 'count': 0}
			
				row["details"].append(score_dict)
		
			row["sort"] = row["score"]*1000000-row["time"];
			scorelist.append(row)
		
		scorelist.sort(key=lambda t: t["sort"], reverse=True)
		i = 1; previous = 0
		for t in scorelist:
			if t["sort"] < previous:
				i += 1
			if t["sort"] > 0:
				t["rank"] = i
				ranks[t["id"]] = i
			else:
				ranks[t["id"]] = '-'
			previous = t["sort"]
		scoreboard.append({"list": scorelist, "name": teamclass.name})

	render = loader.render_to_string('score.html', {"contest": contest, "problems": problems, "scoreboard": scoreboard})
	
	cache.set(create_cache_key("render_scoreboard", is_judge), ranks, 1800)
	cache.set(create_cache_key("ranks", is_judge), ranks, 1800)
		
	return {"render": render, "ranks": ranks}

def render_scoreboard(request, template, is_judge=False):
	contest = Contest.objects.get()
	render = cache.get(create_cache_key("render_scoreboard", is_judge))
	
	if render is None:
		render = get_scoreboard(is_judge)["render"]
	
	return render_to_response(template,
							  {'scoreboard': render},
							  context_instance=RequestContext(request))