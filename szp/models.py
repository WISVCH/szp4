from django.db import models
from django.contrib.auth.models import User

class Contest(models.Model):
	STATUS_CHOICES = (("INITIALIZED", "INITIALIZED"),
					  ("RUNNING", "RUNNING"),
					  ("NOINFO", "NOINFO"),
					  ("STOPPED", "STOPPED"))
	starttime = models.DateTimeField(blank=True, null=True)
	endtime = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=11, choices=STATUS_CHOICES)
	name = models.CharField(max_length=150)
	date = models.DateField()
	location = models.CharField(max_length=50)

	def __unicode__(self):
		return "%s, %s (%s)" % (self.name, self.location, self.date)

class Autojudge(models.Model):
	ip_address = models.IPAddressField()
	def __unicode__(self):
		return "Autojudge %d (%s)" % (self.id, self.ip_address)

class Teamclass(models.Model):
	name = models.CharField(max_length=100)
	rank = models.IntegerField()

	def __unicode__(self):
		return self.name

class Team(models.Model):
	name = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	teamclass = models.ForeignKey(Teamclass)
	organisation = models.CharField(max_length=100)
	id_key = models.CharField(max_length=96)
	ip_address = models.IPAddressField()

	def __unicode__(self):
		return self.name

class Teammember(models.Model):
	team = models.ForeignKey(Team)
	name = models.CharField(max_length=100)
	email = models.EmailField()

	def __unicode__(self):
		return self.name

class Profile(models.Model):
	user = models.ForeignKey(User, unique=True)

	team = models.ForeignKey(Team, null=True, blank=True)
	is_judge = models.BooleanField()

	def __unicode__(self):
		return self.user.username

class File(models.Model):
	content = models.TextField()

	def __unicode__(self):
		return "File<%d>" % (self.id,)

class Problem(models.Model):
	letter = models.CharField(max_length=1, unique=True)
	name = models.CharField(max_length=100)
	colour = models.CharField(max_length=20)
	in_file_name = models.CharField(max_length=20)
	out_file_name = models.CharField(max_length=20)
	in_file = models.OneToOneField(File, related_name="problem_in_file")
	out_file = models.OneToOneField(File, related_name="problem_out_file")
	timelimit = models.IntegerField()
	check_script_file_name = models.CharField(max_length=20)
	check_script_file = models.OneToOneField(File, related_name="problem_check_script_file")

	def __unicode__(self):
		return "%s: %s" % (self.letter, self.name)

class Clarreq(models.Model):
	prob = models.ForeignKey(Problem, null=True, blank=True)
	subject = models.CharField(max_length=80)
	msg = models.TextField()
	sender = models.ForeignKey(Team)
	timestamp = models.DateTimeField(auto_now_add=True)
	read_by = models.ManyToManyField(Profile)

class Clar(models.Model):
	prob = models.ForeignKey(Problem, null=True, blank=True)
	req = models.ForeignKey(Clarreq, null=True, blank=True)
	subject = models.CharField(max_length=765)
	msg = models.TextField()
	receiver = models.ForeignKey(Team)
	timestamp = models.DateTimeField()
	read = models.BooleanField()

class Compiler(models.Model):
	name = models.CharField(max_length=100)
	version = models.CharField(max_length=10)
	extension = models.CharField(max_length=10)
	source_filename = models.CharField(max_length=100)
	compile_line = models.CharField(max_length=100)
	execute_line = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

class FrozenScore(models.Model):
	team = models.ForeignKey(Team)
	prob = models.ForeignKey(Problem)
	submission_count = models.IntegerField()
	score = models.IntegerField()
	time_used = models.IntegerField()

class Submission(models.Model):
	STATUS_CHOICES = (("NEW", "NEW"),
					  ("BEING_JUDGED", "BEING_JUDGED"),
					  ("CHECKED", "CHECKED"),
					  ("VERIFIED", "VERIFIED"))
	problem = models.ForeignKey(Problem)
	compiler = models.ForeignKey(Compiler)
	file = models.OneToOneField(File)
	file_name = models.CharField(max_length=200)
	team = models.ForeignKey(Team)
	status = models.CharField(max_length=12, choices=STATUS_CHOICES)
	autojudge= models.ForeignKey(Autojudge, null=True, blank=True)
	last_status_change = models.DateTimeField(auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "%s by %s (%s)" % (self.problem.letter, self.team.name, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

class Result(models.Model):
	JUDGEMENT_CHOICES = (("NAUGHTY_PROGRAM", "NAUGHTY_PROGRAM"),
						 ("COMPILER_ERROR", "COMPILER_ERROR"),
						 ("RUNTIME_ERROR", "RUNTIME_ERROR"),
						 ("RUNTIME_EXCEEDED", "RUNTIME_EXCEEDED"),
						 ("WRONG_OUTPUT", "WRONG_OUTPUT"),
						 ("NO_OUTPUT", "NO_OUTPUT"),
						 ("ACCEPTED", "ACCEPTED"))

	submission = models.ForeignKey(Submission)
	judgement = models.CharField(max_length=16, choices=JUDGEMENT_CHOICES)
	judged_by = models.ForeignKey(Autojudge)
	# FIXME: Change name to judge_comment
	jury_comment = models.TextField(null=True, blank=True)
	compiler_output_file = models.OneToOneField(File, related_name="result_compiler_output_file")
	submission_output_file = models.OneToOneField(File, null=True, blank=True, related_name="result_submission_output_file")
	autojudge_comment_file = models.OneToOneField(File, null=True, blank=True, related_name="result_autojudge_comment_file")
	check_output_file = models.OneToOneField(File, null=True, blank=True, related_name="result_check_output_file")
	verified_by = models.ForeignKey(Profile, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "%s for %s by %s" % (self.judgement, self.submission.problem.letter, self.submission.team.name)


class Score(models.Model):
	team = models.ForeignKey(Team)
	problem = models.ForeignKey(Problem)
	submission_count = models.IntegerField()
	correct = models.BooleanField()
	time = models.IntegerField(null=True, blank=True)

	def __unicode__(self):
		if self.correct:
			status = "OK"
			time = self.time
		else:
			status = "WRONG"
			time = 0

		return "%s problem %s %s %d (%d)" % (self.team.name, self.problem.letter, status, self.submission_count, time)

