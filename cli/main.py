import sys
import datetime
import string

import argparse
from django.core.exceptions import ObjectDoesNotExist
from szp.models import *

def showcontest(args):
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

def setcontest(args):
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

def addteam(args):
	print "Not yet finished"
	print args

def addproblem(args):
	print args
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

def run():
	parser = argparse.ArgumentParser(description='Sub Zero Programming command line interface')
	subparsers = parser.add_subparsers()

	parser_showcontest = subparsers.add_parser('showcontest')
	parser_showcontest.set_defaults(func=showcontest)

	parser_setcontest = subparsers.add_parser('setcontest')
	parser_setcontest.set_defaults(func=setcontest)
	parser_setcontest.add_argument('status', choices=("INITIALIZED", "RUNNING", "NOINFO", "STOPPED"))
	parser_setcontest.add_argument('date', nargs='?', default=None)
	parser_setcontest.add_argument('name', nargs='?', default=None)
	parser_setcontest.add_argument('location', nargs='?', default=None)

	parser_addteam = subparsers.add_parser('addteam')
	parser_addteam.set_defaults(func=addteam)
	parser_addteam.add_argument('name')
	parser_addteam.add_argument('organisation')
	parser_addteam.add_argument('class')
	parser_addteam.add_argument('location')
	parser_addteam.add_argument('ip')
	parser_addteam.add_argument('member1')
	parser_addteam.add_argument('e-mail1')
	parser_addteam.add_argument('member2', nargs='?', default=None)
	parser_addteam.add_argument('e-mail2', nargs='?', default=None)
	parser_addteam.add_argument('member3', nargs='?', default=None)
	parser_addteam.add_argument('e-mail3', nargs='?', default=None)

	parser_addproblem = subparsers.add_parser('addproblem')
	parser_addproblem.set_defaults(func=addproblem)
	parser_addproblem.add_argument('letter', help='the letter of this problem', choices=string.uppercase)
	parser_addproblem.add_argument('timelimit', help='the timelimit (in seconds) for this problem', type=int)
	parser_addproblem.add_argument('name', help='the name of the problem to add')
	parser_addproblem.add_argument('colour', help='the colour of the balloon for this problem')
	parser_addproblem.add_argument('infile', help='input file used for testing', type=file)
	parser_addproblem.add_argument('outfile', help='ouput file used for testing', type=file)
	parser_addproblem.add_argument('checkscript', help='checker script used to compare the output', type=file)

	args = parser.parse_args()
	args.func(args)
	
