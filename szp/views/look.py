from django.shortcuts import render_to_response
from django.template import RequestContext
from szp.views.general import render_scoreboard

def score(request):
	return render_scoreboard(request, 'look.html')