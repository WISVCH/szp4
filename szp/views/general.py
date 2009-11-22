from szp.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader
from django.utils.http import urlquote

from time import mktime

def index(request):
	return render_to_response('index.html')

def get_scoreboard(is_judge=False):
	contest = Contest.objects.get()
	teams = {}
	problems = Problem.objects.order_by("letter")
	
	if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
		results = Result.objects.select_related("submission").order_by('timestamp')
	else:
		results = Result.objects.filter(timestamp__lt=contest.freezetime).select_related("submission").order_by('timestamp')

	for result in results:
		t = result.submission.team_id
		p = result.submission.problem_id
		
		# print "%s -- %s " % (result.judgement, result.submission)
		
		if t not in teams:
			teams[t] = {}
		
		if p not in teams[t]:
			teams[t][p] = {'count': 1, 'solved': False}
		elif not teams[t][p]['solved']:
			teams[t][p]['count'] += 1
		# else: # Caution: results in extra queries to fetch teamname
			# print "Already solved: %d \t %s" % (result.id, result)

		if teams[t][p]['solved'] == False and result.judgement == "ACCEPTED":
			teams[t][p]['solved'] = True
			teams[t][p]['solved_time'] = result.submission.timestamp
	
	if is_judge:
		teamclasses = Teamclass.objects.order_by("rank")
	else:
		teamclasses = Teamclass.objects.filter(rank__gt=0).order_by("rank")

	scoreboard= []
	for teamclass in teamclasses:
		scorelist = []

		for team in Team.objects.filter(teamclass=teamclass):
			t = team.id
			row = {"name": team.name, "organisation": team.organisation, "score": 0, "time": 0, "details": []}
			for problem in problems:
				p = problem.id
				# solved = "V" if teams[team][problem]['solved'] else ' '
				# print "\t%s: %d %s" % (problem.letter, teams[team][problem]['count'], solved),
				try:
					# if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
					# 	score = Score.objects.get(team=team, problem=p)
					# else:
					# 	score = FrozenScore.objects.get(team=team, problem=p)
					score_dict = {'correct': teams[t][p]['solved'], 'count': teams[t][p]['count']}
					if teams[t][p]['solved']:
						timedelta = (teams[t][p]['solved_time'] - contest.starttime)
						score_dict["time"] = timedelta.days*24 + timedelta.seconds/60
						row["time"] += (teams[t][p]['count'] - 1)*settings.SUBMITFAIL_PENALTY + score_dict["time"]
						row["score"] += 1
				except KeyError:
					score_dict = {'correct': False, 'count': 0}
				
				row["details"].append(score_dict)
			
			scorelist.append(row)
			
		scorelist.sort(key=lambda s: s["score"]*1000000-s["time"], reverse=True)
		scoreboard.append({"list": scorelist, "name": teamclass.name})

	return {"contest": contest, "problems": problems, "scoreboard": scoreboard}

def get_scoreboard2(is_judge=False):
	contest = Contest.objects.get()
	problems = Problem.objects.order_by("letter")

	if is_judge:
		teamclasses = Teamclass.objects.order_by("rank")
	else:
		teamclasses = Teamclass.objects.filter(rank__gt=0).order_by("rank")

	scoreboard= []
	for teamclass in teamclasses:
		scorelist = []

		for team in Team.objects.filter(teamclass=teamclass):
			row = {"name": team.name, "organisation": team.organisation, "class": team.teamclass.name, "score": 0, "time": 0, "details": []}
			for p in problems:
				try:
					if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
						score = Score.objects.get(team=team, problem=p)
					else:
						score = FrozenScore.objects.get(team=team, problem=p)
					score_dict = {'correct': score.correct, 'count': score.submission_count}
					if score.correct:
						score_dict["time"] = score.time
						row["time"] += (score.submission_count - 1)*settings.SUBMITFAIL_PENALTY + score.time
						row["score"] += 1
				except ObjectDoesNotExist:
					score_dict = {'correct': False, 'count': 0}

				row["details"].append(score_dict)

			scorelist.append(row)

		scorelist.sort(key=lambda s: s["score"]*1000000-s["time"], reverse=True)
		scoreboard.append({"list": scorelist, "name": teamclass.name})

	return {"contest": contest, "problems": problems, "scoreboard": scoreboard, "is_judge": is_judge}

def render_scoreboard(request, template, is_judge=False):
	contest = Contest.objects.get()
	
	cache_key = 'scoreboard-' + ('jury-' if is_judge else 'team-') + str(contest.resulttime)
	scoreboard = cache.get(cache_key)
	
	print cache_key
	
	if scoreboard is None:
		scoreboard = loader.render_to_string('score.html', get_scoreboard(is_judge))
		cache.set(cache_key, scoreboard, 10)
	
	return render_to_response(template,
							  {'scoreboard': scoreboard},
							  context_instance=RequestContext(request))