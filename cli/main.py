# main.py
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

import sys
import os
import datetime
import string
import socket
from getpass import getpass

import argparse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Permission
from szp.models import *

class showcontest():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('showcontest')
		parser.set_defaults(obj=self)

	def run(self, args):
		try:
			contest = Contest.objects.get()
		except ObjectDoesNotExist:
			print "No contest set"
			sys.exit(1)
		print "ID:", contest.id
		print "Name:", contest.name
		print "Date:", contest.date
		print "Location:", contest.location
		print "Status:", contest.get_status_display()
		print "Start Time:", contest.starttime
		print "End Time:", contest.endtime

class setcontest():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('setcontest')
		parser.set_defaults(obj=self)
		parser.add_argument('status', choices=("INITIALIZED", "RUNNING", "NOINFO", "STOPPED"))
		parser.add_argument('date', nargs='?', default=None)
		parser.add_argument('name', nargs='?', default=None)
		parser.add_argument('location', nargs='?', default=None)
	
	def run(self, args):
		try:
			contest = Contest.objects.get()
		except ObjectDoesNotExist:
			if not args.date or not args.name or not args.location:
				print "Not enough arguments"
				sys.exit(1)
			contest = Contest()

		if contest.get_status_display() == "INITIALIZED" and args.status == "RUNNING":
			contest.starttime = datetime.datetime.now()

		if args.status == "NOINFO":
			if contest.get_status_display() != "RUNNING":
				print "We first need to be in RUNNING state before going to NOINFO"
				sys.exit(1)
			
			contest.freezetime = datetime.datetime.now()
			
		contest.status = args.status
		if args.date:
			contest.date = args.date
		if args.name:
			contest.name = args.name
		if args.location:
			contest.location = args.location

		contest.save()

class addteamclass():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addteamclass')
		parser.set_defaults(obj=self)
		parser.add_argument('rank')
		parser.add_argument('name')

	def run(self, args):
		teamclass = Teamclass()
		teamclass.name = args.name
		teamclass.rank = args.rank
		teamclass.save()
		
class addteam():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addteam')
		parser.set_defaults(obj=self)
		parser.add_argument('name')
		parser.add_argument('organisation')
		parser.add_argument('teamclass', type=int, help='Teamclass rank')
		parser.add_argument('location')
		parser.add_argument('-ip', help='IP address or resolvable hostname', default=None)
		parser.add_argument('-password', help='User password', default=None)

	def run(self, args):
		team = Team()
		team.name = args.name
		team.organisation = args.organisation
		team.teamclass = Teamclass.objects.get(rank=args.teamclass)
		team.location = args.location
		team.save()
		Contest.objects.get().save() # Updates 'resulttime'
		if args.ip or args.password:
			if args.password:
				user = User(username=team.name.replace(' ', '_'))
				user.set_password(args.password)
			else:
				user = User(username=args.ip.replace('.', '_'))
				user.set_unusable_password()
			user.save()
			
			profile = Profile()
			profile.is_judge = False
			profile.user = user
			profile.team = team
			if args.ip:
				profile.ip_address = socket.gethostbyname(args.ip)
			profile.save()
		else:
			print "Team '%s' has id %d" % (team.name, team.id)

class addproblem():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addproblem')
		parser.set_defaults(obj=self)
		parser.add_argument('letter', help='the letter of this problem', choices=string.uppercase)
		parser.add_argument('timelimit', help='the timelimit (in seconds) for this problem', type=int)
		parser.add_argument('name', help='the name of the problem to add')
		parser.add_argument('colour', help='the colour of the balloon for this problem')
		parser.add_argument('infile', help='input file used for testing', type=file)
		parser.add_argument('outfile', help='ouput file used for testing', type=file)
		parser.add_argument('checkscript', help='checker script used to compare the output', type=file)

	def run(self, args):
		problem = Problem()
		problem.letter = args.letter
		problem.timelimit = args.timelimit
		problem.name = args.name
		problem.colour = args.colour
		problem.in_file_name = os.path.basename(args.infile.name)
		problem.out_file_name = os.path.basename(args.outfile.name)
		problem.check_script_file_name = os.path.basename(args.checkscript.name)
		in_file = File(content=args.infile.read())
		in_file.save()
		problem.in_file = in_file
		out_file = File(content=args.outfile.read())
		out_file.save()
		problem.out_file = out_file
		check_script = File(content=args.checkscript.read())
		check_script.save()
		problem.check_script_file = check_script
		problem.save()
		print 'Added problem %s' % problem
		Contest.objects.get().save() # Updates 'resulttime'

class addcompiler():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addcompiler')
		parser.set_defaults(obj=self)
		parser.add_argument('source_filename', help='the name the source file should be renamed to')
		parser.add_argument('compile_line', help='the command-line to compile the source-file')
		parser.add_argument('execute_line', help='the command-line to run the source-file')
		parser.add_argument('extension', help='the default extension for this compiler (including the dot (.))')
		parser.add_argument('name', help='name of the compiler')
		parser.add_argument('version', help='version of the compiler')

	def run(self, args):
		compiler = Compiler()
		compiler.source_filename = args.source_filename
		compiler.compile_line = args.compile_line
		compiler.execute_line = args.execute_line
		compiler.extension = args.extension
		compiler.name = args.name
		compiler.version = args.version
		compiler.save()

class addautojudge():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addautojudge')
		parser.set_defaults(obj=self)
		parser.add_argument('ip_address', help='IP address or resolvable hostname of the autojudge')

	def run(self, args):
		autojudge = Autojudge()
		autojudge.ip_address = socket.gethostbyname(args.ip_address)
		autojudge.save()

class listautojudges():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('listautojudges')
		parser.set_defaults(obj=self)

	def run(self, args):
		autojudges = Autojudge.objects.all()
		maxwidth_id = max([len(str(a.id)) for a in autojudges]+[len("id")])
		maxwidth_ip = max([len(str(a.ip_address)) for a in autojudges]+[len("ip_address")])
		print "%-*s  %-*s" % (maxwidth_id, "id", maxwidth_ip, "ip address")
		for a in autojudges:
			print "%-*s  %-*s" % (maxwidth_id, a.id, maxwidth_ip, a.ip_address)
		

class listcompilers():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('listcompilers')
		parser.set_defaults(obj=self)

	def run(self, args):
		compilers = Compiler.objects.all()
		maxwidth_id = max([len(str(c.id)) for c in compilers]+[len("id")])
		maxwidth_name = max([len(str(c.name)) for c in compilers]+[len("name")])
		maxwidth_version = max([len(str(c.version)) for c in compilers]+[len("version")])
		maxwidth_extension = max([len(str(c.extension)) for c in compilers]+[len("ext.")])
		maxwidth_source_filename = max([len(str(c.source_filename)) for c in compilers]+[len("src filename")])
		maxwidth_compile_line = max([len(str(c.compile_line)) for c in compilers]+[len("compile line")])
		maxwidth_execute_line = max([len(str(c.execute_line)) for c in compilers]+[len("exec line")])
		print "%-*s  %-*s  %-*s  %-*s  %-*s  %-*s  %-*s" % (maxwidth_id, "id", maxwidth_name, "name", maxwidth_version, "version",
															maxwidth_extension, "ext.", maxwidth_source_filename, "src filename",
															maxwidth_compile_line, "compile_line", maxwidth_execute_line, "exec line")
		for c in compilers:
			print "%-*s  %-*s  %-*s  %-*s  %-*s  %-*s  %-*s" % (maxwidth_id, c.id, maxwidth_name, c.name, maxwidth_version, c.version,
																maxwidth_extension, c.extension, maxwidth_source_filename, c.source_filename,
																maxwidth_compile_line, c.compile_line, maxwidth_execute_line, c.execute_line)
		
class addjudge():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addjudge')
		parser.set_defaults(obj=self)
		parser.add_argument('username', help='Username of judge')
		parser.add_argument('-password', help='Judge password', default=None)
		parser.add_argument('-ip', help='IP address or resolvable hostname of judge', default=None)
		parser.add_argument('-team', help='Team ID for judge', default=0, type=int)

	def run(self, args):
		user = User(username=args.username)
		if args.password:
			user.set_password(args.password)
		else:
			user.set_unusable_password()
		user.save()
		profile = Profile()
		profile.is_judge = True
		profile.user = user
		if args.team:
			profile.team = Team.objects.get(id=args.team)
		if args.ip:
			profile.ip_address = socket.gethostbyname(args.ip)
		profile.save()

def main():
	parser = argparse.ArgumentParser(description='Sub Zero Programming command line interface')
	subparsers = parser.add_subparsers()

	addautojudge(subparsers)
	addcompiler(subparsers)
	addjudge(subparsers)
	addproblem(subparsers)
	addteam(subparsers)
	addteamclass(subparsers)
	listautojudges(subparsers)
	listcompilers(subparsers)
	showcontest(subparsers)
	setcontest(subparsers)

	args = parser.parse_args()
	args.obj.run(args)
