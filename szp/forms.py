from django import forms
from django.forms import ModelChoiceField
from szp.models import *
from django.core.exceptions import ObjectDoesNotExist

class SubmitForm(forms.Form):
	problem = forms.ModelChoiceField(Problem.objects.order_by('letter'), empty_label=u"Choose a problem")
	compiler = forms.ModelChoiceField(Compiler.objects.order_by('name'), empty_label=u"Choose a compiler")
	file = forms.FileField()
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(SubmitForm, self).__init__(*args, **kwargs)
	
	# There is a nice race condition in this check:
	# if two submissions are done close together, this code
	# doesn't yet know the if the submission has been accepted.
	def clean(self):
		cleaned_data = self.cleaned_data
		profile = self.request.user.get_profile()
		contest = Contest.objects.get()
		
		if contest.status != "RUNNING" and contest.status != "NOINFO":
			raise forms.ValidationError("Contest is not running.")
		elif cleaned_data['problem'] and not profile.is_judge:
			problem = cleaned_data['problem']
			submissions = Submission.objects.filter(team=profile.team, problem=problem).order_by("-timestamp")

			for s in submissions:
				if s.result and s.result.judgement == "ACCEPTED":
					raise forms.ValidationError("A submission has already been accepted for this problem.")
		
		return cleaned_data