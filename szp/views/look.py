from szp.views.general import render_scoreboard

def score(request):
	return render_scoreboard(request, 'look.html')