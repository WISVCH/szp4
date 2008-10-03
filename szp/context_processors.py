from szp.models import *
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

def statuswindow(request):
	status = {}
	
	contest = Contest.objects.get()

	try:
		profile = request.user.get_profile()
		
		if profile.is_judge:
			status["new_clarreqs"] = Clarreq.objects.filter(dealt_with=False).count()
		else:
			status["new_clars"] = Clar.objects.filter(receiver=profile.team).filter(read=False).count()
			status["new_results"] = profile.new_results

			scoredict = {}
			
			for team in Team.objects.all():
				scoredict[team] = {"score": 0, "time": 0}

			for score in Score.objects.filter(correct=True):
				scoredict[score.team]["score"] += 1
				scoredict[score.team]["time"] += score.time

			scorelist = []
			for (team, score) in scoredict.items():
				scorelist.append({"team": team, "score": score["score"], "time": score["time"]})
				if team == profile.team:
					ourscore = score["score"]
					ourtime = score["time"]

			for (rank, score) in enumerate(scorelist):
				if score["time"] == ourtime and score["score"] == ourscore:
					status["rank"] = rank+1
					break
				
	except (ObjectDoesNotExist, AttributeError):
		pass
	
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

	return status

