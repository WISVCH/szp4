from django.db import models
from django.contrib.auth.models import User

class Contest(models.Model):
	STATUS_CHOICES = (("INITIALIZED", "INITIALIZED"),
					  ("RUNNING", "RUNNING"),
					  ("NOINFO", "NOINFO"),
					  ("STOPPED", "STOPPED"))
	starttime = models.DateTimeField(blank=True, null=True)
	freezetime = models.DateTimeField(blank=True, null=True)
	endtime = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=11, choices=STATUS_CHOICES)
	name = models.CharField(max_length=150)
	date = models.DateField()
	location = models.CharField(max_length=50)
	
	resulttime = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "%s, %s (%s)" % (self.name, self.location, self.date)

class Autojudge(models.Model):
	ip_address = models.IPAddressField(unique=True)
	def __unicode__(self):
		return "Autojudge %d (%s)" % (self.id, self.ip_address)

class Teamclass(models.Model):
	name = models.CharField(max_length=100,unique=True)
	rank = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'teamclasses'

class Team(models.Model):
	name = models.CharField(max_length=100, unique=True)
	location = models.CharField(max_length=100)
	teamclass = models.ForeignKey(Teamclass)
	organisation = models.CharField(max_length=100)
	new_results = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

class Profile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	team = models.ForeignKey(Team, null=True, blank=True)
	is_judge = models.BooleanField()
	ip_address = models.IPAddressField(null=True, blank=True, unique=True)
	
	def __unicode__(self):
		return self.user.username

	class Meta:
		permissions = (
			("team", "Team"),
			("jury", "Jury"),
		)

class File(models.Model):
	content = models.TextField()

	def __unicode__(self):
		return "File<%d>" % (self.id,)

class Problem(models.Model):
	letter = models.CharField(max_length=1, unique=True)
	name = models.CharField(max_length=100)
	colour = models.CharField(max_length=20)
	in_file = models.OneToOneField(File, related_name="problem_in_file")
	out_file = models.OneToOneField(File, related_name="problem_out_file")
	timelimit = models.IntegerField()
	check_script_file_name = models.CharField(max_length=20)
	check_script_file = models.OneToOneField(File, related_name="problem_check_script_file")

	def __unicode__(self):
		return "%s: %s" % (self.letter, self.name)

class Clarreq(models.Model):
	problem = models.ForeignKey(Problem, null=True, blank=True)
	subject = models.CharField(max_length=80)
	message = models.TextField()
	sender = models.ForeignKey(Team)
	timestamp = models.DateTimeField(auto_now_add=True)
	dealt_with = models.BooleanField()

class Clar(models.Model):
	problem = models.ForeignKey(Problem, null=True, blank=True)
	subject = models.CharField(max_length=80)
	message = models.TextField()
	receiver = models.ForeignKey(Team)
	timestamp = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField()

class Sentclar(models.Model):
	problem = models.ForeignKey(Problem, null=True, blank=True)
	subject = models.CharField(max_length=80)
	message = models.TextField()
	receiver = models.ForeignKey(Team, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

class Compiler(models.Model):
	name = models.CharField(max_length=100)
	version = models.CharField(max_length=10)
	extension = models.CharField(max_length=10)
	source_filename = models.CharField(max_length=100)
	compile_line = models.CharField(max_length=100)
	execute_line = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

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
		return "[%s] %s by %s (%s)" % (self.status, self.problem.letter, self.team.name, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

class Result(models.Model):
	JUDGEMENT_CHOICES = (("NAUGHTY_PROGRAM", "NAUGHTY_PROGRAM"),
						 ("COMPILER_ERROR", "COMPILER_ERROR"),
						 ("RUNTIME_ERROR", "RUNTIME_ERROR"),
						 ("RUNTIME_EXCEEDED", "RUNTIME_EXCEEDED"),
						 ("WRONG_OUTPUT", "WRONG_OUTPUT"),
						 ("NO_OUTPUT", "NO_OUTPUT"),
						 ("ACCEPTED", "ACCEPTED"))

	submission = models.OneToOneField(Submission, primary_key=True)
	judgement = models.CharField(max_length=16, choices=JUDGEMENT_CHOICES)
	judged_by = models.ForeignKey(Autojudge)
	judge_comment = models.TextField(null=True, blank=True)
	compiler_output_file = models.OneToOneField(File, related_name="result_compiler_output_file")
	submission_output_file = models.OneToOneField(File, null=True, blank=True, related_name="result_submission_output_file")
	autojudge_comment_file = models.OneToOneField(File, null=True, blank=True, related_name="result_autojudge_comment_file")
	check_output_file = models.OneToOneField(File, null=True, blank=True, related_name="result_check_output_file")
	verified_by = models.ForeignKey(User, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "%s for %s by %s" % (self.judgement, self.submission.problem.letter, self.submission.team.name)