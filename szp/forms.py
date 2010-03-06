# forms.py
# Copyright (C) 2008-2009 Jeroen Dekkers <jeroen@dekkers.cx>
# Copyright (C) 2008-2010 Mark Janssen <mark@ch.tudelft.nl>
#
# This file is part of SZP.
# 
# SZP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# SZP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with SZP.  If not, see <http://www.gnu.org/licenses/>.

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
		if profile.is_judge:
			return cleaned_data
		
		contest = Contest.objects.get()
		
		if contest.status != "RUNNING" and contest.status != "NOINFO":
			raise forms.ValidationError("Contest is not running.")
		elif cleaned_data['problem']:
			problem = cleaned_data['problem']
			submissions = Submission.objects.filter(team=profile.team, problem=problem).order_by("-timestamp")

			for s in submissions:
				if s.result and s.result.judgement == "ACCEPTED":
					raise forms.ValidationError("A submission has already been accepted for this problem.")
		
		return cleaned_data