# admin.py
# Copyright (C) 2008-2009 Jeroen Dekkers <jeroen@dekkers.cx>
# Copyright (C) 2008-2009 Mark Janssen <mark@ch.tudelft.nl>
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

from szp.models import *
from django.contrib import admin

admin.site.register(Autojudge)
admin.site.register(Teamclass)
admin.site.register(Team)
admin.site.register(File)
admin.site.register(Problem)
admin.site.register(Clarreq)
admin.site.register(Clar)
admin.site.register(Sentclar)
admin.site.register(Compiler)
admin.site.register(Contest)
admin.site.register(Result)
admin.site.register(Profile)
admin.site.register(Submission)
