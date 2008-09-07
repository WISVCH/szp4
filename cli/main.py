import sys
import datetime
import string

import argparse
from django.core.exceptions import ObjectDoesNotExist
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

		contest.status = args.status
		if args.date:
			contest.date = args.date
		if args.name:
			contest.name = args.name
		if args.location:
			contest.location = args.location

		contest.save()

class addteam():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addteam')
		parser.set_defaults(obj=self)
		parser.add_argument('name')
		parser.add_argument('organisation')
		parser.add_argument('class')
		parser.add_argument('location')
		parser.add_argument('ip')
		parser.add_argument('member1')
		parser.add_argument('e-mail1')
		parser.add_argument('member2', nargs='?', default=None)
		parser.add_argument('e-mail2', nargs='?', default=None)
		parser.add_argument('member3', nargs='?', default=None)
		parser.add_argument('e-mail3', nargs='?', default=None)

	def run(self, args):
		print "Not yet finished"
		print args

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
		problem.in_file_name = args.infile.name
		problem.out_file_name = args.outfile.name
		problem.check_script_file_name = args.checkscript.name
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

class addcompiler():
	def __init__(self, subparsers):
		parser = subparsers.add_parser('addcompiler')
		parser.set_defaults(obj=self)
		parser.add_argument('source_filename', help='the name the source file should be renamed to')
		parser.add_argument('compile_line', help='the command-line to compile the source-file')
		parser.add_argument('execute_line', help='the command-line to run the source-file')
		parser.add_argument('extension', help='the default extension for this compiler (including the dot (.))')
		parser.add_argument('name', help='name of the compiler')
		parser.add_argument('version', help='optional version of the compiler')

	def run(self, args):
		compiler = Compiler()
		compiler.source_filename = args.source_filename
		compiler.compile_line = args.compile_line
		compiler.execute_line = args.execute_line
		compiler.extension = args.extension
		compiler.name = args.name
		compiler.version = args.version
		compiler.save()

def main():
	parser = argparse.ArgumentParser(description='Sub Zero Programming command line interface')
	subparsers = parser.add_subparsers()

	parser_showcontest = subparsers.add_parser('showcontest')
	parser_showcontest.set_defaults(func=showcontest)

	parser_addteam = subparsers.add_parser('addteam')
	parser_addteam.set_defaults(func=addteam)

	addcompiler(subparsers)
	addproblem(subparsers)
	addteam(subparsers)
	showcontest(subparsers)
	setcontest(subparsers)

	args = parser.parse_args()
	args.obj.run(args)
	
