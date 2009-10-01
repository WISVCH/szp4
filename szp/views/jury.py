from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from szp.models import *
from szp.forms import *
from django.core.exceptions import ObjectDoesNotExist
from team import gettime
from datetime import datetime
from szp.views.general import get_scoreboard

@login_required
def home(request):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')
	

	return render_to_response('jury_home.html',
							  {"profile": profile},
							  context_instance=RequestContext(request))

@login_required
def status(request):
	return render_to_response('jury_status.html',
							  context_instance=RequestContext(request))

@login_required
def score(request):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	return render_to_response('jury_score.html',
							  get_scoreboard(jury=True),
							  context_instance=RequestContext(request))

@login_required
def clarification(request):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	if request.method == 'POST':
		if request.POST['team'] != "global":
			teamlist = [Team.objects.get(id=request.POST['team'])]
		else:
			teamlist = Team.objects.all()

		if request.POST['problem'] != "General":
			problem = Problem.objects.get(letter=request.POST['problem'])
		else:
			problem = None

		for team in teamlist:
			clar = Clar()
			clar.problem = problem
			clar.subject = request.POST['subject']
			clar.message = request.POST['message']
			clar.receiver = team
			clar.read = False
			clar.save()
		
		sentclar = Sentclar()
		sentclar.problem = problem
		sentclar.subject = request.POST['subject']
		sentclar.message = request.POST['message']
		if request.POST['team'] != "global":
			sentclar.receiver = team
		sentclar.save()

		return HttpResponseRedirect('/jury/clarification/sent/%s/' % sentclar.id)

	problemlist = Problem.objects.order_by("letter")
	teamlist = Team.objects.order_by("name")

	total_sent = Sentclar.objects.count()
	total_general = Clarreq.objects.filter(problem=None).count()
	total_general_unhandled = Clarreq.objects.filter(problem=None).filter(dealt_with=False).count()

	total = total_general
	total_unhandled = total_general_unhandled

	prob_clarreqs = []
	for problem in problemlist:
		num = Clarreq.objects.filter(problem=problem).count()
		total += num
		unhandled = Clarreq.objects.filter(problem=problem).filter(dealt_with=False).count()
		total_unhandled += unhandled
		row = {"num": num,
			   "unhandled": unhandled,
			   "problem": problem}
		prob_clarreqs.append(row)

	return render_to_response('jury_clarification.html',
							  {"problemlist": problemlist, "teamlist": teamlist, 'total_sent': total_sent,
							   "total": total, "total_unhandled": total_unhandled,
							   "total_general": total_general, "total_general_unhandled": total_general_unhandled,
							   "prob_clarreqs": prob_clarreqs},
							  context_instance=RequestContext(request))

@login_required
def clarification_list(request, which):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	contest = Contest.objects.get()
	problemlist = Problem.objects.order_by("letter")
	teamlist = Team.objects.order_by("name")

	select = None

	if which == "all":
		clars = Clarreq.objects.order_by("-timestamp")
		title = "All"
	elif which == "sent":
		clars = Sentclar.objects.order_by("-timestamp")
		title = "Sent clarifications"
	elif which == "general":
		clars = Clarreq.objects.filter(problem=None).order_by("-timestamp")
		title = "General"
	else:
		problem = Problem.objects.get(letter=which)
		clars = Clarreq.objects.filter(problem=problem).order_by("-timestamp")
		title = str(problem)
		select = problem.letter

	clarlist = []
	for c in clars:
		row = {"time": gettime(c.timestamp, contest), "subject": c.subject }
		if which == "sent":
			row["url"] = "sent/"+str(c.id)
			row["unhandled"] = False
			row["from"] = False
		else:
			row["url"] = c.id
			row["unhandled"] = not c.dealt_with
			row["from"] = c.sender.name

		clarlist.append(row)

	return render_to_response('jury_clarification_list.html',
							  {"problemlist": problemlist, "teamlist": teamlist, 'title': title,
							   'select': select, "clarlist": clarlist},
							  context_instance=RequestContext(request))
		
@login_required
def clarification_show_sent(request, which):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	contest = Contest.objects.get()

	clar = Sentclar.objects.get(id=which)
	sentclar = {"subject": clar.subject,
				"message": clar.message}
	
	if clar.problem:
		sentclar["problem"] = clar.problem
	else:
		sentclar["problem"] = "General"

	if clar.receiver:
		sentclar["to"] = clar.receiver.name
	else:
		sentclar["to"] = "Global"
	
	clars = Sentclar.objects.order_by("-timestamp")
	clarlist = []
	for c in clars:
		row = {"time": gettime(c.timestamp, contest), "subject": c.subject }
		row["url"] = "sent/"+str(c.id)
		clarlist.append(row)

	return render_to_response('jury_clarification_sent.html',
							  {"sentclar": sentclar, "clarlist": clarlist},
							  context_instance=RequestContext(request))
	
	
@login_required
def clarification_show(request, which):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	if request.method == 'POST':
		print request.POST
		if request.POST['button'] == "Dealt With":
			clar = Clarreq.objects.get(id=which)
			clar.dealt_with = True
			clar.save()
		elif request.POST['button'] == "Reply":
			return HttpResponseRedirect('/jury/clarification/%s/reply/' % which)

	contest = Contest.objects.get()

	clar = Clarreq.objects.get(id=which)
	clarreq = {"subject": clar.subject,
			   "message": clar.message,
			   "sender": clar.sender,
			   "unhandled": not clar.dealt_with}
	
	if clar.problem:
		clarreq["problem"] = clar.problem
	else:
		clarreq["problem"] = "General"

	clars = Clarreq.objects.filter(problem=clar.problem).order_by("-timestamp")
	clarlist = []
	for c in clars:
		row = {"time": gettime(c.timestamp, contest), "subject": c.subject }
		row["url"] = c.id
		row["unhandled"] = not c.dealt_with
		row["from"] = c.sender.name
		clarlist.append(row)

	return render_to_response('jury_clarification_show.html',
							  {"clarreq": clarreq, "clarlist": clarlist},
							  context_instance=RequestContext(request))

@login_required
def clarification_reply(request, which):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	if request.method == 'POST':
		clarreq = Clarreq.objects.get(id=which)

		clar = Clar()
		clar.problem = clarreq.problem
		clar.subject = request.POST['subject']
		clar.message = request.POST['message']
		clar.receiver = clarreq.sender
		clar.read = False
		clar.save()
		
		sentclar = Sentclar()
		sentclar.problem = clarreq.problem
		sentclar.subject = request.POST['subject']
		sentclar.message = request.POST['message']
		sentclar.receiver = clarreq.sender
		sentclar.save()

		clarreq.dealt_with = True
		clarreq.save()
		
		return HttpResponseRedirect('/jury/clarification/sent/%s/' % sentclar.id)
		

	contest = Contest.objects.get()
	clarreq = Clarreq.objects.get(id=which)

	reply = {"to": clarreq.sender,
			 "subject": "Re: "+clarreq.subject}

	if clarreq.problem:
		reply["problem"] = clarreq.problem
	else:
		reply["problem"] = "General"

	message = clarreq.sender.name+" wrote:\n"
	for line in clarreq.message.splitlines(True):
		message += "> "
		message += line

	message += "\n\nPlease read the problem specification more carefully."

	reply["message"] = message

	clars = Clarreq.objects.filter(problem=clarreq.problem).order_by("-timestamp")
	clarlist = []
	for c in clars:
		row = {"time": gettime(c.timestamp, contest), "subject": c.subject }
		row["url"] = c.id
		row["unhandled"] = not c.dealt_with
		row["from"] = c.sender.name
		clarlist.append(row)

	return render_to_response('jury_clarification_reply.html',
							  {"reply": reply, "clarlist": clarlist},
							  context_instance=RequestContext(request))


@login_required
def submission(request):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	problems = Problem.objects.order_by("letter")
	total = Submission.objects.count()
	problemlist = []

	for p in problems:
		count = Submission.objects.filter(problem=p).count()
		row = {'letter': p.letter, 'name': p.name, 'count': count}
		problemlist.append(row)
	
	return render_to_response('jury_submission.html',
							  {'total': total, 'problemlist': problemlist},
							  context_instance=RequestContext(request))

@login_required
def submission_list(request, problem):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	contest = Contest.objects.get()

	if problem == "all":
		title = "List of all submissions"
		submissions = Submission.objects.order_by("-timestamp")
	else:
		title = "List of submissions for problem "+problem
		submissions = Submission.objects.filter(problem__letter=problem).order_by("-timestamp")

	submissionlist = []
	for s in submissions:
		row = {}
		
		try:
			result = s.result_set.get()
			row['judgement'] = result.judgement
			if result.verified_by:
				row['verified_by'] = result.verified_by.user.username
			else:
				row['verified_by'] = ""
		except ObjectDoesNotExist:
			row['judgement'] = "Pending..."
			row['verified_by'] = ""

		row.update({'time': gettime(s.timestamp, contest), 'id': s.id,
					'problem': s.problem, 'filename': s.file_name, 'team': s.team,
					'compiler': s.compiler.name})
		
		submissionlist.append(row)

	return render_to_response('jury_submission_list.html',
							  {'title': title, 'submissionlist': submissionlist},
							  context_instance=RequestContext(request))

@login_required
def submission_details(request, number):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	submission = Submission.objects.get(id=number)

	if request.method == 'POST':
		if "verify" in request.POST:
			result = submission.result_set.get()
			result.verified_by = profile
			submission.status = "VERIFIED"
			result.save()
			submission.save()
		elif "save" in request.POST:
			result = submission.result_set.get()
			result.judge_comment = request.POST["text"]
			result.save()
			
	contest = Contest.objects.get()
		
	time = gettime(submission.timestamp, contest)

	def cap_output(output):
		cap = 10000
		cap_msg = "SZP Notice: output capped, download file to see everything.\n\n"
		return cap_msg + output[:cap] + "[snip]" if len(output) > cap else output

	program_code = submission.file.content
	problem_input = cap_output(submission.problem.in_file.content)
	expected_output = cap_output(submission.problem.out_file.content)
	
	try:
		result = submission.result_set.get()
		judgement = result.judgement
		if result.verified_by:
			verified_by = result.verified_by.user.username
		else:
			verified_by = None
		compiler_output = result.compiler_output_file.content

		if result.judge_comment:
			judge_comment = result.judge_comment
		else:
			judge_comment = ""

		if result.submission_output_file:
			submission_output = cap_output(result.submission_output_file.content)
		else:
			submission_output = ""

		if result.check_output_file:
			output_diff = cap_output(result.check_output_file.content)
		else:
			output_diff = ""

		if result.autojudge_comment_file:
			autojudge_comment = cap_output(result.autojudge_comment_file.content)
		else:
			autojudge_comment = ""

		has_result = True
	except ObjectDoesNotExist:
		judgement = "Pending..."
		verified_by = None
		compiler_output = ""
		submission_output = ""
		output_diff = ""
		judge_comment = ""
		autojudge_comment = ""
		has_result = False
	
	return render_to_response('jury_submission_details.html',
							  {'time': time, 'submission': submission,
							   'judgement': judgement, 'verified_by': verified_by,
							   'program_code': program_code, 'problem_input': problem_input,
							   'expected_output': expected_output, 'compiler_output': compiler_output,
							   'submission_output': submission_output, 'output_diff': output_diff,
							   'judge_comment': judge_comment, 'autojudge_comment': autojudge_comment,
							   'has_result': has_result,
							   },
							  context_instance=RequestContext(request))


def submission_changeresult(request, number):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	# TODO: We might want to be able to manually accept submissions
	contest = Contest.objects.get()
	submission = Submission.objects.get(id=number)
	if request.method == 'POST':
		result = submission.result_set.get()
		result.judgement = request.POST["judgement"]
		
		team = submission.team
		team.new_results = True
		team.save()
		
		result.save()

		return HttpResponseRedirect('/jury/submission/%s/' % number)

	time = gettime(submission.timestamp, contest)

	try:
		result = submission.result_set.get()
		judgement = result.judgement
		if result.verified_by:
			verified_by = result.verified_by.user.username
		else:
			verified_by = None
	except ObjectDoesNotExist:
		judgement = "Pending..."
		verified_by = None

	judgementlist = []
	for j in Result.JUDGEMENT_CHOICES:
		if judgement == j[0]:
			judgementlist.append({"name": j[0], "selected": True})
		else:
			judgementlist.append({"name": j[0], "selected": False})

	return render_to_response('jury_submission_changeresult.html',
							  {'time': time, 'submission': submission,
							   'judgement': judgement, 'verified_by': verified_by,
							   'judgementlist': judgementlist,
							   },
							  context_instance=RequestContext(request))

def submission_download(request, number, what):
	profile = request.user.get_profile()
	if not profile.is_judge:
		return HttpResponseRedirect('/team/')

	submission = Submission.objects.get(id=number)
	result = submission.result_set.get()

	if what == 'problem_input':
		output = submission.problem.in_file.content
	elif what == 'output_diff' and result.check_output_file:
		output = result.check_output_file.content
	elif what == 'expected_output':
		output = submission.problem.out_file.content
	elif what == 'submission_output' and result.submission_output_file:
		output = result.submission_output_file.content
	elif what == 'compiler_output':
		output = result.compiler_output_file.content
	elif what == 'program_code':
		what = 'program_code_' + submission.file_name
		output = submission.file.content
	elif what == 'autojudge_comment':
		output = result.autojudge_comment_file.content
	else:
		raise Http404
	
	response = HttpResponse(output, mimetype='text/plain')
	response['Content-Disposition'] = 'attachment; filename=%s_%s' % (number, what)
	return response

