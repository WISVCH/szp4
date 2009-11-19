from szp.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.shortcuts import render_to_response

def index(request):
	return render_to_response('index.html')

def get_scoreboard(jury=False):
	contest = Contest.objects.get()
	problems = Problem.objects.order_by("letter")
	
	if jury:
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
					if jury or contest.status == "INITIALIZED" or contest.status == "RUNNING":
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

	return {"contest": contest, "problems": problems, "scoreboard": scoreboard}