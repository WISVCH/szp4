from szp.models import *
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

class IpBackend(ModelBackend):
	"""
	Authenticates against django.contrib.auth.models.User, using IP
	addresses configured in SZP profile.
	"""
	def authenticate(self, ip_address=None):
		if not ip_address:
			return None
		try:
			team = Team.objects.get(ip_address=ip_address)
			user = team.profile_set.get().user
			return user
		except ObjectDoesNotExist:
			return None
