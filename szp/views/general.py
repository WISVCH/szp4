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

def check_judge(user):
	profile = user.get_profile()
	return profile.is_judge

def get_scoreboard(is_judge=False):	
	contest = Contest.objects.get()
	
	if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
		cache_key = 'get_scoreboard-' + ('jury-' if is_judge else 'team-') + str(contest.resulttime)
	else:
		cache_key = 'get_scoreboard-NOINFO'
	response = cache.get(cache_key)
	
	if response is None:
		teams = {}
		problems = Problem.objects.order_by("letter")
	
		if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
			results = Result.objects.select_related("submission").order_by('timestamp')
		else:
			results = Result.objects.filter(submission__timestamp__lt=contest.freezetime)\
				.select_related("submission").order_by('timestamp')

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

		scoreboard = []
		for teamclass in teamclasses:
			scorelist = []

			for team in Team.objects.filter(teamclass=teamclass).order_by("name"):
				t = team.id
				row = {"name": team.name, "organisation": team.organisation, "score": 0, "time": 0, "details": []}
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
				previous = t["sort"]
			scoreboard.append({"list": scorelist, "name": teamclass.name})

		response = {"contest": contest, "problems": problems, "scoreboard": scoreboard}
		cache.set(cache_key, response, 10)
		
	return response

def render_scoreboard(request, template, is_judge=False):
	contest = Contest.objects.get()
	
	if is_judge or contest.status == "INITIALIZED" or contest.status == "RUNNING":
		cache_key = 'render_scoreboard-' + ('jury-' if is_judge else 'team-') + str(contest.resulttime)
	else:
		cache_key = 'render_scoreboard-NOINFO'
	scoreboard = cache.get(cache_key)
	
	if scoreboard is None:
		scoreboard = loader.render_to_string('score.html', get_scoreboard(is_judge))
		cache.set(cache_key, scoreboard, 10)
	
	return render_to_response(template,
							  {'scoreboard': scoreboard},
							  context_instance=RequestContext(request))