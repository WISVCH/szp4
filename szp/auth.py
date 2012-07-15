from szp.models import Profile
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
            user = Profile.objects.get(ip_address=ip_address).user
            return user
        except ObjectDoesNotExist:
            return None
