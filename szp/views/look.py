from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from szp.models import *
from szp.forms import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from szp.views.general import get_scoreboard

def score(request):
	return render_to_response('look.html',
							  get_scoreboard(),
							  context_instance=RequestContext(request))