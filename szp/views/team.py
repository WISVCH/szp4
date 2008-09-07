from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from szp.models import *

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
    return render_to_response('team_submission.html', context_instance=RequestContext(request))

