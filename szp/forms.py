from django import forms
from django.forms import ModelChoiceField
from szp.models import *

class SubmitForm(forms.Form):
	problem = forms.ModelChoiceField(Problem.objects.order_by('letter'), empty_label=u"Choose a problem")
	compiler = forms.ModelChoiceField(Compiler.objects.order_by('name'), empty_label=u"Choose a compiler")
	file = forms.FileField()
