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

class Judge(models.Model):
	judge_name = models.CharField(max_length=765)
	username = models.CharField(max_length=765)
	password = models.CharField(max_length=765)

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
	read_by = models.ManyToManyField(Judge)

class Clar(models.Model):
	prob = models.ForeignKey(Problem, null=True, blank=True)
	req = models.ForeignKey(Clarreq, null=True, blank=True)
	subject = models.CharField(max_length=765)
	msg = models.TextField()
	receiver = models.ForeignKey(Team)
	timestamp = models.DateTimeField()
	read = models.BooleanField()

class Compiler(models.Model):
	compiler_name = models.CharField(max_length=765)
	version = models.CharField(max_length=765)
	extension = models.CharField(max_length=765)
	source_filename = models.CharField(max_length=765)
	compile_line = models.CharField(max_length=765)
	execute_line = models.CharField(max_length=765)

class FrozenScore(models.Model):
	team = models.ForeignKey(Team)
	prob = models.ForeignKey(Problem)
	submission_count = models.IntegerField()
	score = models.IntegerField()
	time_used = models.IntegerField()

class Submission(models.Model):
	problem = models.ForeignKey(Problem)
	compiler = models.ForeignKey(Compiler)
	file = models.OneToOneField(File)
	file_name = models.CharField(max_length=200)
	team = models.ForeignKey(Team)
	status = models.TextField()
	last_status_change = models.DateTimeField()
	timestamp = models.DateTimeField(auto_now_add=True)

class Result(models.Model):
	sub = models.ForeignKey(Submission)
	result = models.TextField()
	comment_file = models.OneToOneField(File, null=True, blank=True, related_name="result_comment_file")
	compile_output_file = models.OneToOneField(File, related_name="result_compile_output_file")
	run_output_file = models.OneToOneField(File, related_name="result_run_output_file")
	check_output_file = models.OneToOneField(File, related_name="result_check_output_file")
	auto_comment_file = models.OneToOneField(File, related_name="result_auto_comment_file")
	judged_by = models.ForeignKey(Autojudge, null=True, blank=True)
	verified_by = models.ForeignKey(Judge, null=True,  blank=True)
	timestamp = models.DateTimeField()

class Score(models.Model):
	team = models.ForeignKey(Team)
	problem = models.ForeignKey(Problem)
	submission_count = models.IntegerField()
	score = models.IntegerField()
	time_used = models.IntegerField()

class Profile(models.Model):
	user = models.ForeignKey(User, unique=True)

	team = models.ForeignKey(Team, null=True, blank=True)
	judge = models.ForeignKey(Judge, null=True, blank=True)

	def __unicode__(self):
		return self.user.username
