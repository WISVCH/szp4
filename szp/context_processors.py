from szp.models import *
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from szp.views.team import getrank

def statuswindow(request):
	status = {}
	
	contest = Contest.objects.get()
	
	print request.path[1:5]
	# try:
	profile = request.user.get_profile()
	
	# if profile.is_judge:
	if request.path[1:5] == 'jury':
		status["new_clarreqs"] = Clarreq.objects.filter(dealt_with=False).count()
	else:
		status["new_clars"] = Clar.objects.filter(receiver=profile.team).filter(read=False).count()
		status["new_results"] = profile.new_results
		status["rank"] = getrank(profile.team)
				
	# except (ObjectDoesNotExist, AttributeError):
	# 	pass
	
	if contest.status == "INITIALIZED":
		status["status_time"] = "WAIT"
	elif contest.status == "STOPPED":
		status["status_time"] = "STOPPED"
	else:
		timedelta = datetime.now() - contest.starttime
		hours = timedelta.days*24+timedelta.seconds / 3600
		minutes = timedelta.seconds % 3600 / 60
		status["status_time"]  = "%02d:%02d" % (hours, minutes)	

	status["status"] = contest.status

	return {'s': status }

