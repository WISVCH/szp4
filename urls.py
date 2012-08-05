# urls.py
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

from django.conf.urls import patterns, url, include
from django.conf import settings
#from django.views.generic import list_detail
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'szp.views.general.index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^look/$', 'szp.views.look.score'),
    url(r'^jury/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'django.views.generic.simple.redirect_to', {'url': '/jury/'}),
)

# FIXME: accounts/profile should point to different things for team and judge
urlpatterns += patterns('szp.views.team',
    url(r'^team/$', 'home'),
    url(r'^accounts/login/$', 'teamlogin'),
    url(r'^team/submitscript/$', 'submitscript'),
    url(r'^team/infoscript/$', 'infoscript'),
    url(r'^team/score/$', 'score'),
    url(r'^team/clarification/$', 'clarification'),
    url(r'^team/clarification/([A-Z]|all|general|sent)/$', 'clarification_list'),
    url(r'^team/clarification/sent/(\d+)/$', 'clarification_sent'),
    url(r'^team/clarification/(\d+)/$', 'clarification_show'),
    url(r'^team/submission/$', 'submission'),
    url(r'^team/status/$', 'status'),
)

urlpatterns += patterns('szp.views.jury',
    url(r'^jury/$', 'home'),
    url(r'^jury/score/$', 'score'),
    url(r'^jury/clarification/$', 'clarification'),
    url(r'^jury/clarification/([A-Z]|all|general|sent)/$', 'clarification_list'),
    url(r'^jury/clarification/sent/(\d+)/$', 'clarification_show_sent'),
    url(r'^jury/clarification/(\d+)/$', 'clarification_show'),
    url(r'^jury/clarification/(\d+)/reply/$', 'clarification_reply'),
    url(r'^jury/submission/$', 'submission'),
    url(r'^jury/submission/([A-Z]|all)/$', 'submission_list'),
    url(r'^jury/submission/(\d+)/$', 'submission_details'),
    url(r'^jury/submission/(\d+)/download/(\w+)$', 'submission_download'),
    url(r'^jury/submission/(\d+)/changeresult/$', 'submission_changeresult'),
    url(r'^jury/status/$', 'status'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    )
