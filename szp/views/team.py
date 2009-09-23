from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import *
from szp.models import *
from szp.forms import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from szp.views.general import calc_scoreboard

def gettime(timestamp, contest):
	if contest.status == "INITIALIZED":
		return "00:00:00"
	timedelta = timestamp - contest.starttime
	hours = timedelta.days*24+timedelta.seconds / 3600
	minutes = timedelta.seconds % 3600 / 60
	seconds = timedelta.seconds % 60
	return "%02d:%02d:%02d" % (hours, minutes, seconds)	


def getrank(ourteam):
	contest = Contest.objects.get()

	scoredict = {}
			
	for team in Team.objects.filter(teamclass=ourteam.teamclass):
		scoredict[team] = {"score": 0, "time": 0}

	if contest.status == "INITIALIZED" or contest.status == "RUNNING":
		for score in Score.objects.filter(correct=True, team__teamclass=ourteam.teamclass):
			scoredict[score.team]["score"] += 1
			scoredict[score.team]["time"] += (score.submission_count - 1)*20 + score.time
	else:
		for score in FrozenScore.objects.filter(correct=True, team__teamclass=ourteam.teamclass):
			scoredict[score.team]["score"] += 1
			scoredict[score.team]["time"] += (score.submission_count - 1)*20 + score.time

	scorelist = []
	for (team, score) in scoredict.items():
		scorelist.append({"team": team, "score": score["score"], "time": score["time"]})
		if team == ourteam:
			ourscore = score["score"]
			ourtime = score["time"]

	scorelist.sort(key=lambda s: s["score"]*1000000-s["time"], reverse=True)

	for (rank, score) in enumerate(scorelist):
		if score["time"] == ourtime and score["score"] == ourscore:
			ourrank = rank+1
			break

	return ourrank

def infoscript(request):
	problems = Problem.objects.order_by('letter')
	compilers = Compiler.objects.order_by('id')
	
	return render_to_response('infoscript',
							  {"problems": problems, "compilers": compilers, })

def submitscript(request):
	ip_address = request.META['REMOTE_ADDR']
	user = authenticate(ip_address=ip_address)
	if user is not None and user.is_active:
		if not 'problem' in request.POST or not 'compiler' in request.POST or not 'submission' in request.POST or not 'filename' in request.POST:
			return render_to_response('submitscript', {"message": "Missing POST variables"})
		try:
			problem = Problem.objects.get(letter=request.POST['problem'])
		except:
			return render_to_response('submitscript', {"message": "ERROR: Invalid problem"})
		
		try:
			compiler = Compiler.objects.get(id=request.POST['compiler'])
		except:
			return render_to_response('submitscript', {"message": "ERROR: Invalid compiler"})

		submission = Submission()
		submission.status = "NEW"
		profile = user.get_profile()
		submission.team = profile.team

		submission.problem = problem
 		submission.compiler = compiler

 		submission.file_name = request.POST['filename']
 		# FIXME: Check upload size
 		file = File()
 		file.content = request.POST['submission']
 		file.save()
 		submission.file = file
 		submission.save()

		return render_to_response('submitscript', {"message": "Submission successful"})
	else:
		return HttpResponseRedirect('/look/')

def teamlogin(request):
	ip_address = request.META['REMOTE_ADDR']
	user = authenticate(ip_address=ip_address)
	if user is not None:
		if user.is_active:
			login(request, user)
			return HttpResponseRedirect('/team/')
		else:
			return HttpResponseRedirect('/look/')

	return HttpResponseRedirect('/jury/login/')

@login_required
def home(request):
	profile = request.user.get_profile()
	return render_to_response('team_home.html',
							  {"profile": profile},
							  context_instance=RequestContext(request))

@login_required
def status(request):
	profile = request.user.get_profile()
	contest = Contest.objects.get()
	
	new_clars = Clar.objects.filter(receiver=profile.team).filter(read=False).count()
	new_results = profile.new_results
	
	scoredict = {}
	
	for team in Team.objects.all():
		scoredict[team] = {"score": 0, "time": 0}
		
	if contest.status == "INITIALIZED" or contest.status == "RUNNING":
		for score in Score.objects.filter(correct=True):
			scoredict[score.team]["score"] += 1
			scoredict[score.team]["time"] += score.time
	else:
		for score in FrozenScore.objects.filter(correct=True):
			scoredict[score.team]["score"] += 1
			scoredict[score.team]["time"] += score.time

	rank = getrank(profile.team)
	
	if contest.status == "INITIALIZED":
		status_time = "WAIT"
	elif contest.status == "STOPPED":
		status_time = "STOPPED"
	else:
		timedelta = datetime.now() - contest.starttime
		hours = timedelta.days*24+timedelta.seconds / 3600
		minutes = timedelta.seconds % 3600 / 60
		status_time  = "%02d:%02d" % (hours, minutes)	

	return render_to_response('team_status.html',
							  {"new_results": new_results, "new_clars": new_clars,
							   "status_time": status_time, "rank": rank},
							  context_instance=RequestContext(request))

@login_required
def score(request):
	contest = Contest.objects.get()
	problems = Problem.objects.order_by("letter")

	scoreboard = calc_scoreboard()

	return render_to_response('team_score.html', {"contest": contest, "problems":problems, "scoreboard": scoreboard,
												  "colcount": 5+len(problems)},
							  context_instance=RequestContext(request))

@login_required
def clarification(request):
	profile = request.user.get_profile()
	team = profile.team

	if request.method == 'POST':
		# FIXME: Make a django form for this.
		problem = request.POST['problem']
		subject = request.POST['subject']
		body = request.POST['body']

		clarreq = Clarreq()
		if problem != "General":
			clarreq.problem = Problem.objects.get(letter=problem)
		clarreq.subject = subject
		clarreq.message = body
		clarreq.sender = team
		clarreq.dealt_with = False
		clarreq.save()

		return HttpResponseRedirect('/team/clarification/sent/%s/' % clarreq.id)

	problemlist = Problem.objects.order_by("letter")

	total_sent = Clarreq.objects.filter(sender=team).count()

	total_general = Clar.objects.filter(problem=None).filter(receiver=team).count()
	total_general_new = Clar.objects.filter(problem=None).filter(receiver=team).filter(read=False).count()

	total = total_general
	total_new = total_general_new

	prob_clars = []
	for problem in problemlist:
		num = Clar.objects.filter(problem=problem).filter(receiver=team).count()
		total += num
		new = Clar.objects.filter(problem=problem).filter(receiver=team).filter(read=False).count()
		total_new += new
		row = {"num": num,
			   "new": new,
			   "problem": problem}
		prob_clars.append(row)

	return render_to_response('team_clarification.html',
							  {"problemlist": problemlist, "team": team,
							   "total": total, "total_new": total_new, "total_sent": total_sent,
							   "total_general": total_general, "total_general_new": total_general_new,
							   "prob_clars": prob_clars},
							  context_instance=RequestContext(request))


@login_required
def clarification_list(request, which):
	contest = Contest.objects.get()
	problemlist = Problem.objects.order_by("letter")
	profile = request.user.get_profile()
	team = profile.team

	select = None

	if which == "all":
		clars = Clar.objects.filter(receiver=team).order_by("-timestamp")
		title = "All"
	elif which == "sent":
		clars = Clarreq.objects.filter(sender=team).order_by("-timestamp")
		title = "Sent clarifications"
	elif which == "general":
		clars = Clar.objects.filter(receiver=team).filter(problem=None).order_by("-timestamp")
		title = "General"
	else:
		problem = Problem.objects.get(letter=which)
		clars = Clar.objects.filter(receiver=team).filter(problem=problem).order_by("-timestamp")
		title = str(problem)
		select = problem.letter

	clarlist = []
	for c in clars:
		row = {"time": gettime(c.timestamp, contest), "subject": c.subject }
		if which == "sent":
			row["url"] = "sent/"+str(c.id)
			row["new"] = False
		else:
			row["url"] = c.id
			row["new"] = not c.read

		clarlist.append(row)

	return render_to_response('team_clarification_list.html',
							  {"problemlist": problemlist, "team": team,
							   "title": title, "clarlist": clarlist, "select": select},
							  context_instance=RequestContext(request))


@login_required
def clarification_sent(request, clarid):
	profile = request.user.get_profile()
	clarreq = Clarreq.objects.get(id=clarid)
	contest = Contest.objects.get()

	if not clarreq.problem:
		problem = "General"
	else:
		problem = str(clarreq.problem)

	ourclars = Clarreq.objects.filter(sender=profile.team).order_by("-timestamp")
	
	clarlist = []
	for c in ourclars:
		row = {'id': c.id, 'time': gettime(c.timestamp, contest), 'subject': c.subject}
		clarlist.append(row)

	return render_to_response('team_clarification_sent.html',
							  {"profile": profile, "clarreq": clarreq, "problem": problem, "clarlist": clarlist},
							  context_instance=RequestContext(request))

@login_required
def clarification_show(request, which):
	contest = Contest.objects.get()
	profile = request.user.get_profile()
	team = profile.team

	c = Clar.objects.get(id=which)
	if c.receiver != team:
		return HttpResponseRedirect('/team/clarification/')

	c.read = True
	c.save()

	clar = {"subject": c.subject,
			"message": c.message}
	
	if c.problem:
		clar["problem"] = c.problem
	else:
		clar["problem"] = "General"

	clars = Clar.objects.filter(receiver=team).filter(problem=c.problem).order_by("-timestamp")
	clarlist = []
	for c in clars:
		row = {"time": gettime(c.timestamp, contest), "subject": c.subject }
		row["url"] = c.id
		row["new"] = not c.read
		clarlist.append(row)

	return render_to_response('team_clarification_show.html',
							  {"clar": clar, "clarlist": clarlist},
							  context_instance=RequestContext(request))

@login_required
def submission(request, problem=None):
	profile = request.user.get_profile()
	contest = Contest.objects.get()
	if request.method == 'POST':
		if contest.status != "RUNNING" and contest.status != "NOINFO":
			return HttpResponseRedirect('/team/')
		
		form = SubmitForm(request.POST, request.FILES)
		if form.is_valid():
			# FIXME: Check contest state
			# FIXME: Check whether we already have an accepted solution for this problem
			# FIXME: Maybe check whether extension is correct.
			submission = Submission()
			submission.status = "NEW"
			submission.team = profile.team

			submission.problem = form.cleaned_data['problem']
			submission.compiler = form.cleaned_data['compiler']

			submission.file_name = request.FILES['file'].name
			# FIXME: Check upload size
			file = File()
			content = request.FILES['file'].read()
			try:
				file.content = content.decode("utf-8")
			except UnicodeError:
				file.content = content.decode("iso8859-1")
				
			file.save()
			submission.file = file
			submission.save()
			
			return HttpResponseRedirect('/team/submission/')

	else:
		form = SubmitForm()

	profile.new_results = False
	profile.save()

	submissions = Submission.objects.filter(team=profile.team).order_by("-timestamp")

	result_list = []

	for s in submissions:
		try:
			judgement = s.result_set.get().judgement
		except ObjectDoesNotExist:
			judgement = "Pending..."
			
		r = {'time': gettime(s.timestamp, contest), 'problem': s.problem, 'judgement': judgement}
		result_list.append(r)

	return render_to_response('team_submission.html',
							  {"profile": profile, 'form': form, 'results': result_list},
							  context_instance=RequestContext(request))
