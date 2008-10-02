from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from szp.models import *
from szp.forms import *
from django.core.exceptions import ObjectDoesNotExist

@login_required
def home(request):
	profile = request.user.get_profile()
	teammembers = profile.team.teammember_set.all()
	return render_to_response('team_home.html',
							  {"profile": profile, "teammembers": teammembers},
							  context_instance=RequestContext(request))

@login_required
def status(request):
	profile = request.user.get_profile()
	teammembers = profile.team.teammember_set.all()
	return render_to_response('team_status.html',
							  {"profile": profile, "teammembers": teammembers},
							  context_instance=RequestContext(request))

@login_required
def score(request):
	contest = Contest.objects.get()
	problems = Problem.objects.order_by("letter")

	scorelist = []
	for team in Team.objects.all():
		row = {"name": team.name, "organisation": team.organisation, "class": team.teamclass.name, "score": 0, "time": 0, "details": []}
		for p in problems:
			try:
				score = Score.objects.get(team=team, problem=p)
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

	print scorelist
 	
	return render_to_response('team_score.html', {"contest": contest, "problems":problems, "scorelist": scorelist},
							  context_instance=RequestContext(request))

@login_required
def clarification(request):
    return render_to_response('team_clarification.html', context_instance=RequestContext(request))

@login_required
def submission(request, problem=None):
	profile = request.user.get_profile()
	if request.method == 'POST':
		form = SubmitForm(request.POST, request.FILES)
		if form.is_valid():
			# FIXME: Check contest state
			# FIXME: Check whether extension is correct.
			# FIXME: Check whether we already have an accepted solution for this problem
			submission = Submission()
			submission.status = "NEW"
			submission.team = profile.team

			submission.problem = form.cleaned_data['problem']
			submission.compiler = form.cleaned_data['compiler']

			submission.file_name = request.FILES['file'].name
			# FIXME: Check upload size
			file = File()
			file.content = request.FILES['file'].read()
			file.save()
			submission.file = file
			submission.save()
			
			return HttpResponseRedirect('/team/submission/')

	else:
		form = SubmitForm()

	contest = Contest.objects.get()

	submissions = Submission.objects.filter(team=profile.team).order_by("-timestamp")

	result_list = []

	for s in submissions:
		try:
			judgement = s.result_set.get().judgement
		except ObjectDoesNotExist:
			judgement = "Pending..."
			
		timedelta = s.timestamp - contest.starttime
		hours = timedelta.days*24+timedelta.seconds / 3600
		minutes = timedelta.seconds % 3600 / 60
		seconds = timedelta.seconds % 60
		r = {'time': "%02d:%02d:%02d" % (hours, minutes, seconds), 'problem': s.problem, 'judgement': judgement}
		result_list.append(r)

	return render_to_response('team_submission.html',
							  {"profile": profile, 'form': form, 'results': result_list},
							  context_instance=RequestContext(request))
