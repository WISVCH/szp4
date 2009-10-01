from django.shortcuts import render_to_response
from django.template import RequestContext
from szp.views.general import get_scoreboard

def score(request):
	return render_to_response('look.html',
							  get_scoreboard(),
							  context_instance=RequestContext(request))