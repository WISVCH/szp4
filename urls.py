from django.conf.urls.defaults import *
from django.conf import settings
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
    (r'^look/$', 'szp.views.look.score'),
)

# FIXME: accounts/profile should point to different things for team and judge
urlpatterns += patterns('szp.views.team',
	(r'^accounts/profile/$', 'home'),
    (r'^team/$', 'home'),
    (r'^team/infoscript$', 'infoscript'),
	(r'^team/score/$', 'score'),
    (r'^team/clarification/$', 'clarification'),
    (r'^team/clarification/([A-Z]|all|general|sent)/$', 'clarification_list'),
    (r'^team/clarification/sent/(\d+)/$', 'clarification_sent'),
    (r'^team/clarification/(\d+)/$', 'clarification_show'),
    (r'^team/submission/$', 'submission'),
	(r'^team/status/$', 'status'),
)

urlpatterns += patterns('szp.views.jury',
    (r'^jury/$', 'home'),
	(r'^jury/score/$', 'score'),
    (r'^jury/clarification/$', 'clarification'),
    (r'^jury/clarification/([A-Z]|all|general|sent)/$', 'clarification_list'),
    (r'^jury/clarification/sent/(\d+)/$', 'clarification_show_sent'),
    (r'^jury/clarification/(\d+)/$', 'clarification_show'),
    (r'^jury/clarification/(\d+)/reply/$', 'clarification_reply'),
    (r'^jury/submission/$', 'submission'),
    (r'^jury/submission/([A-Z]|all)/$', 'submission_list'),
    (r'^jury/submission/(\d+)/$', 'submission_details'),
    (r'^jury/submission/(\d+)/changeresult/$', 'submission_changeresult'),
	(r'^jury/status/$', 'status'),
					  
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    )
