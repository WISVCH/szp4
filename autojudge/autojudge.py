#!/usr/bin/python

import os
import sys
import shutil
import time
from subprocess import Popen, PIPE, STDOUT
import stat
import socket

# This will insert the parent duriectory to the path so we can import
# settings.
sys.path.insert(0, os.path.normpath(sys.path[0]+"/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from szp.models import *

autojudge = None

def uploadresult(submission, judgement, compiler_output, submission_output=None, autojudge_comment=None, check_output=None):
	result = Result()
	result.submission = submission
	result.judgement = judgement
	result.judged_by = autojudge

	compiler_output_file = File(content=compiler_output)
	compiler_output_file.save()
	result.compiler_output_file = compiler_output_file

	if submission_output:
		submission_output_file = File()
		try:
			submission_output_file.content = submission_output.decode("utf-8")
		except UnicodeError:
			submission_output_file.content = submission_output.decode("iso8859-1")
		submission_output_file.save()
		result.submission_output_file = submission_output_file

	if autojudge_comment:
		autojudge_comment_file = File(content=autojudge_comment)
		autojudge_comment_file.save()
		result.autojudge_comment_file = autojudge_comment_file

	if check_output:
		check_output_file = File()
		try:
			check_output_file.content = check_output.decode("utf-8")
		except UnicodeError:
			check_output_file.content = check_output.decode("iso8859-1")
		check_output_file.save()
		result.check_output_file = check_output_file

	result.save()
	submission.status = "CHECKED"
	submission.save()

	try:
		score = Score.objects.get(team=submission.team, problem=submission.problem)
	except ObjectDoesNotExist:
		score = Score(team=submission.team, problem=submission.problem, submission_count=0, correct=False)

	score.submission_count += 1
	if judgement == "ACCEPTED":
		score.correct = True
		contest = Contest.objects.get()
		timedelta = (submission.timestamp - contest.starttime)
		score.time = timedelta.days*24 + timedelta.seconds/60

	score.save()

	team = submission.team.get()
	team.new_results = True
	team.save()

if __name__ == '__main__':
	ip_address = sys.argv[1] if len(sys.argv) > 1 else socket.gethostbyname(socket.gethostname())
	
	try:
		autojudge = Autojudge.objects.get(ip_address=ip_address)
	except ObjectDoesNotExist:
		print "No autojudge found with IP address %s, exiting" % ip_address
		sys.exit(1)
	print "We are", autojudge
	while True:
		try:
			submission = Submission.objects.filter(status="NEW").order_by("timestamp")[0]
			# For testing
			#submission = Submission.objects.order_by("timestamp")[0]
		except IndexError:
			# No pending submission, sleep and try again.
			sys.stdout.write('.')
			sys.stdout.flush()
			time.sleep(5)
			continue
			

		submission.status = "BEING_JUDGED"
		submission.autojudge = autojudge
		id = submission.id
		submission.save()

		# We now sleep for a moment and fetch the submission again
		# from the database. In the case another autojudge got this
		# submission at the same time, autojudge would be set to
		# the other autojudge and we won't judge it.
		time.sleep(0.1)
		try:
			submission = Submission.objects.filter(id=submission.id, autojudge=autojudge).get()
		except ObjectDoesNotExist:
			print "Can't find submission we are supposed to judge, probably a rare race condition"
			continue

		testdir = os.path.join(os.getcwd(),"testdir")
		if os.path.exists(testdir):
			shutil.rmtree(testdir)
		os.mkdir(testdir)

		source_file_name = os.path.join(testdir, submission.compiler.source_filename.replace("${LETTER}", submission.problem.letter))
		fp = open(source_file_name, "w")
		fp.write(submission.file.content.encode("utf-8"))
		fp.close()

		in_file_name = os.path.join(testdir, submission.problem.in_file_name)
		fp = open(in_file_name, "w")
		fp.write(submission.problem.in_file.content)
		fp.close()

		print "Starting to judge submission from %s for problem %s, submitted at %s" % (submission.id, submission.problem.letter, submission.timestamp)
		
		cmd = submission.compiler.compile_line.replace("${LETTER}", submission.problem.letter).split()

		compile = Popen(cmd, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=testdir)
		compile.wait()

		compiler_output = compile.stdout.read()

		if compile.returncode != 0:
			uploadresult(submission, "COMPILER_ERROR", compiler_output)
			print "COMPILER_ERROR"
			continue

		# FIXME: This should go in some configuration file
		env = {}

		# The maximum file size a submission can create. [64 MiB]
		env['WATCHDOG_LIMIT_FSIZE']="67108864"
		
		# The maximum amount of virtual memory a submission can use. [1024 MiB]
		env['WATCHDOG_LIMIT_AS']="1073741824"
		
		# The maximum amount of spawned processes. [16]
		env['WATCHDOG_LIMIT_NPROC']="16"
		
		# FIXME: We shouldn't hardcode this
		cmd=['/home/szp/szp4/autojudge/watchdog',
			 submission.compiler.execute_line.replace("${LETTER}", submission.problem.letter),
			 str(submission.problem.timelimit)]

		output_filename = os.path.join(testdir, 'submission_output')
		output = open(output_filename, "w+")

		input_fd = open(in_file_name, "r")

	        devnull = open("/dev/null", "w+")

		run = Popen(cmd, stdin=input_fd, stdout=output, stderr=devnull, close_fds=True, cwd=testdir, env=env)
		run.wait()

		devnull.close()
		output.seek(0)
		submission_output = output.read()
		output.close()
		watchdog = open(os.path.join(testdir, "watchdog_output"), "r")
		watchdog_output = watchdog.read()
		watchdog.close()

		# FIXME We currently don't implement backtraces of core dumps.

		if run.returncode == 1 or run.returncode == 2:
			uploadresult(submission, "RUNTIME_ERROR", compiler_output, submission_output, watchdog_output)
			print "RUNTIME_ERROR"
			continue
		elif run.returncode == 3:
			uploadresult(submission, "RUNTIME_EXCEEDED", compiler_output, submission_output, watchdog_output)
			print "RUNTIME_EXCEEDED"
			continue
		elif run.returncode != 0:
			print "AUTOJUDGE ERROR: WATCHDOG RETURNED UNKOWN VALUE: %d" % run.returncode
			sys.exit(1)
		
		if len(submission_output) == 0:
			uploadresult(submission, "NO_OUTPUT", compiler_output, submission_output, watchdog_output)
			print "NO_OUTPUT"
			continue

		out_file_name = os.path.join(testdir, submission.problem.out_file_name)
		fp = open(out_file_name, "w")
		fp.write(submission.problem.out_file.content)
		fp.close()
		
		check_script_file_name = os.path.join(testdir, submission.problem.check_script_file_name)
		fp = open(check_script_file_name, "w")
		fp.write(submission.problem.check_script_file.content)
		fp.close()

		os.chmod(check_script_file_name, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

		cmd = [check_script_file_name, output_filename, out_file_name]
		check = Popen(cmd, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=testdir, env=env)
		check.wait()

		check_output = check.stdout.read()
		
		if check.returncode == 0:
			uploadresult(submission, "ACCEPTED", compiler_output, submission_output, watchdog_output, check_output)
			print "ACCEPTED"
		elif check.returncode == 1 or check.returncode == 2:
			uploadresult(submission, "WRONG_OUTPUT", compiler_output, submission_output, watchdog_output, check_output)
			print "WRONG_OUTPUT"
		else:
			print "AUTOJUDGE ERROR: CHECKSCRIPT RETURNED UNKNOWN VALUE"
			sys.exit(1)

		print "Submission judged."
		
