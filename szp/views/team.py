from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from szp.models import *
from szp.forms import *

@login_required
def home(request):
	profile = request.user.get_profile()
	teammembers = profile.team.teammember_set.all()
	return render_to_response('team_home.html',
							  {"profile": profile, "teammembers": teammembers},
							  context_instance=RequestContext(request))

@login_required
def score(request):
	contest = Contest.objects.get()
	return render_to_response('team_score.html', {"contest": contest}, context_instance=RequestContext(request))

@login_required
def clarification(request):
    return render_to_response('team_clarification.html', context_instance=RequestContext(request))

@login_required
def submission(request):
	profile = request.user.get_profile()
	if request.method == 'POST':
		form = SubmitForm(request.POST, request.FILES)
		if form.is_valid():
			# FIXME: Check whether extension is correct.
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
			
			return HttpResponseRedirect('/team/submission/'+submission.problem.letter+'/')

	else:
		form = SubmitForm()
	
	return render_to_response('team_submission.html',
							  {"profile": profile, 'form': form},
							  context_instance=RequestContext(request))
