from django.conf.urls.defaults import *
from django.conf import settings
#from django.contrib.auth.views import login, logout
#from django.views.generic import list_detail
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^szp4/', include('szp4.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
)

urlpatterns += patterns('szp.views.team',
	(r'^accounts/profile/$', 'home'),
    (r'^team/$', 'home'),
	(r'^team/score/$', 'score'),
    (r'^team/clarification/$', 'clarification'),
    (r'^team/submit/$', 'submit'),
)
    
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    )
