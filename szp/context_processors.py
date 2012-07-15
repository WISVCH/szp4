# context_processors.py
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

from szp.models import Clar, Clarreq, Contest
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from szp.views.team import getrank


def statuswindow(request):
    status = {}

    contest = Contest.objects.get()

    try:
        profile = request.user.get_profile()

        if profile.is_judge and request.path[1:5] == 'jury':
            status["new_clarreqs"] = Clarreq.objects.filter(dealt_with=False).count()
        else:
            status["new_clars"] = Clar.objects.filter(receiver=profile.team).filter(read=False).count()
            status["new_results"] = profile.team.new_results
            status["rank"] = getrank(profile.team, profile.is_judge)
            status["team_id"] = profile.team.id

    except (ObjectDoesNotExist, AttributeError):
        pass

    if contest.status == "INITIALIZED":
        status["status_time"] = "WAIT"
    elif contest.status == "STOPPED":
        status["status_time"] = "STOPPED"
    else:
        timedelta = datetime.now() - contest.starttime
        hours = timedelta.days * 24 + timedelta.seconds / 3600
        minutes = timedelta.seconds % 3600 / 60
        status["status_time"] = "%02d:%02d" % (hours, minutes)

    status["status"] = contest.status

    return {'s': status, 'c': contest}
