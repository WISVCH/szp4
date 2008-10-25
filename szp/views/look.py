from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from szp.models import *
from szp.forms import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from szp.views.general import calc_scoreboard

def score(request):
	contest = Contest.objects.get()
	problems = Problem.objects.order_by("letter")

	scoreboard = calc_scoreboard()

	if contest.status == "INITIALIZED":
		status_time = "WAIT"
	elif contest.status == "STOPPED":
		status_time = "STOPPED"
	else:
		timedelta = datetime.now() - contest.starttime
		hours = timedelta.days*24+timedelta.seconds / 3600
		minutes = timedelta.seconds % 3600 / 60
		status_time  = "%02d:%02d" % (hours, minutes)	

	return render_to_response('look.html', {"contest": contest, "problems":problems, "colcount": 5+len(problems),
											"scoreboard": scoreboard, "status_time": status_time},
							  context_instance=RequestContext(request))
