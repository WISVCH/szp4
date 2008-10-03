from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from szp.models import *
from szp.forms import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

def score(request):
	contest = Contest.objects.get()
	problems = Problem.objects.order_by("letter")

	scorelist = []
	for team in Team.objects.all():
		row = {"name": team.name, "organisation": team.organisation, "class": team.teamclass.name, "score": 0, "time": 0, "details": []}
		for p in problems:
			try:
				if contest.status == "INITIALIZED" or contest.status == "RUNNING":
					score = Score.objects.get(team=team, problem=p)
				else:
					score = FrozenScore.objects.get(team=team, problem=p)
				score_dict = {'correct': score.correct, 'count': score.submission_count}
				if score.correct:
					# FIXME: 20 shouldn't be hard-coded here
					score_dict["time"] = score.time
					row["time"] += (score.submission_count - 1)*20 + score.time
					row["score"] += 1
			except ObjectDoesNotExist:
				score_dict = {'correct': False, 'count': 0}

			row["details"].append(score_dict)

		scorelist.append(row)

	scorelist.sort(key=lambda s: s["score"]*1000000-s["time"], reverse=True)

	if contest.status == "INITIALIZED":
		status_time = "WAIT"
	elif contest.status == "STOPPED":
		status_time = "STOPPED"
	else:
		timedelta = datetime.now() - contest.starttime
		hours = timedelta.days*24+timedelta.seconds / 3600
		minutes = timedelta.seconds % 3600 / 60
		status_time  = "%02d:%02d" % (hours, minutes)	

	return render_to_response('look.html', {"contest": contest, "problems":problems,
											"scorelist": scorelist, "status_time": status_time},
							  context_instance=RequestContext(request))
