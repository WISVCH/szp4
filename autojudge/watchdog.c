/*
 *  watchdog.c
 *  Copyright (C) 2008 Jeroen Dekkers <jeroen@dekkers.cx>
 *  Copyright (C) 2004 Sjoerd Hemminga
 *  Copyright (C) 1999, 2001 Joris van Rantwijk
 *
 *  Written by Joris van Rantwijk, Dec 1999, Nov 2001
 *  Very minor modifications by Sjoerd Hemminga, Jun 2004
 *
 *  This file is part of SZP.
 *
 *  SZP is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  SZP is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with SZP; if not, write to the Free Software Foundation, Inc.,
 *  51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/*
 *  Execute a program in a safe environment for a limited amount of time.
 *
 *  Syntax: watchdog <command> <timelimit>
 *
 *  <command>       Command to be executed as child
 *                  (use quotes if the command contains more than one word).
 *  <timelimit>     Maximum running time in seconds.
 *                  Specify 0 to disable the timelimit.
 *
 *  Watchdog starts the specified command, and waits until the child process
 *  either exits by itself or exceeds the time limit. The program can be
 *  forced to abort by pressing CTRL-C; watchdog will then stop the process
 *  and proceed as if the time limit was exceeded. Note that watchdog
 *  measures the total elapsed time, not just the CPU time. This means that
 *  the amount of CPU time available to the program may depend on the system
 *  load.
 *
 *  Stdin and stdout will be passed through to the child program, watchdog
 *  never uses stdin or stdout. Watchdog will print informational messages
 *  and error messages on stderr. Normally:
 *    watchdog: hh:mm:ss program started ...
 *    watchdog: hh:mm:ss program exited normally (exit status <n>)
 *    watchdog: hh:mm:ss program exited on signal <n> (<signalname>)
 *    watchdog: hh:mm:ss time limit exceeded
 *    watchdog; hh:mm:ss aborted by user
 *    watchdog: hh:mm:ss finished (<x.xx>s elapsed)
 *
 *  The exit status indicates how the program ended:
 *    0  program exited normally with exit status 0
 *    1  program exited normally with exit status != 0
 *    2  program exited on a signal
 *    3  program was aborted after exceeding the time limit
 *    4  watchdog encountered an error
 *
 *  The child program runs with special user and group ids, to prevent it
 *  from fiddling with the rest of the system. For this, we use the uid
 *  and primary gid from the user specified as SAFE_USERNAME at compile time.
 *  This also means you should pay attention to file and directory permissions
 *  to make sure that the executable file and any additional files are
 *  accessible to the SAFE_USERNAME user.
 *  Note: On most systems, programs can always create files in directories
 *  like /tmp /var/tmp and /var/lock; watchdog does nothing to prevent this.
 *
 *  Watchdog can optionally set resource limits for the child program. When
 *  the program exceeds these limits, system calls will fail and the program
 *  will most likely crash. The limits can be set in environment variables:
 *  WATCHDOG_LIMIT_FSIZE = maximum written file size in bytes
 *  WATCHDOG_LIMIT_AS    = maximum amount of virtual memory in bytes
 *  WATCHDOG_LIMIT_NPROC = maximum amount of spawned processes (or threads)
 *  If a variable is undefined, watchdog will set no limit for it.
 *
 *  After the child program finishes, watchdog kills _all_ processes with
 *  the same user id to make sure that any child processes are gone.
 *  This could cause problems if other applications are using the same
 *  user / group ids. We therefore recommend against using a standard
 *  username (like the 'nobody' account). Instead, you should set up a
 *  dedicated account for this (like 'szpexec').
 *
 *  The watchdog executable must be owned by root, and have the setuid bit
 *  enabled. For security reasons, it should not be world executable, and it
 *  should certainly not be writable by anyone but root. We recommend
 *  something like this:
 *  -rwsr-x---   1 root     szp         16384 Mar  9  1978 watchdog*
 *
 */

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <sys/signal.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/resource.h>

#define SAFE_USERNAME "szpexec"

#define EXIT_ALL_OK		0
#define EXIT_NONZERO_STATUS	1
#define EXIT_KILLED_BY_SIGNAL	2
#define EXIT_LIMIT_EXCEEDED	3
#define EXIT_INTERNAL_ERROR	4

#define DEFAULT_SHELL		"/bin/sh"


static struct {
	const int resource;
	const char * const envname;
	int present;
	unsigned long value;
} resource_limit[4] = {
  { RLIMIT_FSIZE, "WATCHDOG_LIMIT_FSIZE", 0, 0 },
  { RLIMIT_AS,    "WATCHDOG_LIMIT_AS"   , 0, 0 },
  { RLIMIT_NPROC, "WATCHDOG_LIMIT_NPROC", 0, 0 },
  { 0, NULL, 0, 0 }
};

char *command;
unsigned int timelimit;

uid_t safe_uid;
uid_t safe_gid;
char *use_shell;

struct timeval starttime;
struct timeval endtime;

int normal_exit;
int exit_status;
volatile int limit_exceeded = 0;
volatile int aborted_by_user = 0;


/*
 *  Print a message on stderr.
 */
void mesg(char *format, ...)
{
	time_t now;
	struct tm *local;
	char timestr[80];
	va_list args;

	now = time(NULL);
	local = localtime(&now);
	strftime(timestr, 80, "%H:%M:%S", local);
	fprintf(stderr, "watchdog: %s ", timestr);
	va_start(args, format);
	vfprintf(stderr, format, args);
	va_end(args);
	fprintf(stderr, "\n");
	fflush(stderr);
}


/*
 *  Print message on stderr and exit.
 */
void fatal(char *format, ...)
{
	va_list args;
	fprintf(stderr, "watchdog: ERROR: ");
	va_start(args, format);
	vfprintf(stderr, format, args);
	va_end(args);
	fprintf(stderr, "\n");
	exit(EXIT_INTERNAL_ERROR);
}


/*
 *  Find the user id and primary group id of SAFE_USERNAME.
 */
void lookup_safe_user(void)
{
	struct passwd *pw;
	pw = getpwnam(SAFE_USERNAME);
	if (pw == NULL)
		fatal("cannot find user %s", SAFE_USERNAME);
	safe_uid = pw->pw_uid;
	safe_gid = pw->pw_gid;
	endpwent();
}


/*
 *  Parse resource limit settings from environment and unset
 *  corresponding environment variables.
 */
void parse_resource_limits(void)
{
	const char *envname;
	char *val, *p;
	int i;

	for (i = 0; resource_limit[i].envname != NULL; i++) {
		envname = resource_limit[i].envname;
		val = getenv(envname);
		if (val == NULL || *val == 0) {
			mesg("WARNING: No setting for %s", envname);
		} else {
			unsetenv(envname);
			resource_limit[i].present = 1;
			resource_limit[i].value = strtoul(val, &p, 10);
			if (p == NULL || p == val || *p != 0)
				fatal("Invalid setting for %s", envname);
		}
	}
}


/*
 *  Main section of the child process.
 */
void child_main(void)
{
	char *argv[5];
	int i;

	/* Drop all privileges */

	if ( initgroups(SAFE_USERNAME, safe_gid) != 0 )
		fatal("cannot set supplemental groups");
	endgrent();
	if ( setgid(safe_gid) != 0 )
		fatal("cannot set safe gid");
	if ( setuid(safe_uid) != 0 )
		fatal("cannot set safe uid");

	/* Set resource limits */

	for (i = 0; resource_limit[i].envname != NULL; i++) {
		if (resource_limit[i].present) {
			struct rlimit rlim;
			rlim.rlim_cur = resource_limit[i].value;
			rlim.rlim_max = resource_limit[i].value;
			if (setrlimit(resource_limit[i].resource, &rlim) != 0)
				mesg("WARNING: setrlimit failed for %s",
				     resource_limit[i].envname);
		}
	}

	/* Execute command */

	argv[0] = use_shell;
	if (strrchr(use_shell, '/'))
		argv[0] = strrchr(use_shell, '/') + 1;
	argv[1] = "-c";
	argv[2] = command;
	argv[3] = NULL;

	execv(use_shell, argv);

	fatal("exec failed (%s)", strerror(errno));
}


/*
 *  Handle SIGALRM and SIGINT signals by setting the limit_exceeded flag.
 */
static void sig_handler(int sig)
{
	limit_exceeded = 1;
	if (sig != SIGALRM)
		aborted_by_user = 1;
}


/*
 *  Main program.
 */
int main(int argc, char *argv[])
{
	struct sigaction act;
	int status;
	pid_t prog_pid;
	long elapsedsec, elapsedusec;

	/* Check program arguments. */

	if (argc != 3)
		fatal("Syntax: watchdog <command> <timelimit>");

	command = argv[1];

	{ char *p = NULL;
	  timelimit = strtoul(argv[2], &p, 10);
	  if (p == NULL || p == argv[2] || *p != 0)
	  	fatal("");
	}

	/* Check user id. */

	if (geteuid() != 0)
		fatal("effective uid != 0 (must be setuid root)");
	if (getuid() == 0)
		fatal("real uid == 0 (must not be started as root)");

	/* Determine values for safe_uid and safe_gid. */

	lookup_safe_user();

	if (safe_uid == 0)
		fatal("safe_uid == 0 (dangerous)");
	if (safe_gid == 0)
		fatal("safe_gid == 0 (dangerous)");
	if (safe_uid == getuid())
		fatal("safe uid == real uid (started by untrusted user)");

	/* Determine which shell we will use. */

	use_shell = getenv("SHELL");
	if (use_shell == NULL || use_shell[0] == '\0')
		use_shell = DEFAULT_SHELL;

	/* Get resource limits from environment */

	parse_resource_limits();

	/* Start execution thread. */

	prog_pid = fork();
	if (prog_pid == 0)
		child_main();
	else if (prog_pid < 0)
		fatal("fork failed (%s)", strerror(errno));

	close(STDIN_FILENO);
	close(STDOUT_FILENO);

	gettimeofday(&starttime, NULL);

	mesg("program started command=\"%s\", timelimit=%d, pid=%u",
	     command, timelimit, prog_pid);

	/* Set alarm and wait for execution to complete.
	   It is important that the waitpid call will be interrupted by
	   SIGINT or SIGALRM signals, so the SA_RESTART flag must NOT
	   be used. This also means we can't use the ANSI signal function. */

	act.sa_handler = sig_handler;
	sigemptyset(&act.sa_mask);
	act.sa_flags = 0;
	act.sa_restorer = NULL;
	sigaction(SIGALRM, &act, NULL);
	sigaction(SIGINT, &act, NULL);

	alarm(timelimit);

	if ( waitpid(prog_pid, &status, 0) == prog_pid ) {
		alarm(0);
		if ( WIFEXITED(status) ) {
			normal_exit = 1;
			exit_status = WEXITSTATUS(status);
			mesg("program exited normally (status = %d)",
			     exit_status);
		} else if ( WIFSIGNALED(status) ) {
			normal_exit = 0;
			mesg("program exited on signal %d (%s)%s",
			     WTERMSIG(status), strsignal(WTERMSIG(status)),
			     WCOREDUMP(status) ? " (core dumped)" : "");
		} else {
			normal_exit = 0;
			mesg("program exited for unknown reason");
		}
	}

	gettimeofday(&endtime, NULL);

	if (aborted_by_user)
		mesg("aborted by user");
	else if (limit_exceeded)
		mesg("time limit exceeded");

	/* Kill any child processes that are still running.
	   This introduces a tiny race condition: a child could kill us after
	   we drop privileges, just before we get a chance to kill him. */

	if ( setreuid(safe_uid, safe_uid) != 0 )
		fatal("Cannot change uid");

	kill(-1, SIGKILL);

	/* Show elapsed time. */

	elapsedsec = endtime.tv_sec - starttime.tv_sec;
	elapsedusec = endtime.tv_usec - starttime.tv_usec;
	if (elapsedusec < 0) {
		elapsedsec--;
		elapsedusec += 1000000;
	}

	mesg("finished (%ld.%02lds elapsed)",
	     elapsedsec, elapsedusec / 10000);

	/* Return to calling program. */

	if (limit_exceeded)
		return EXIT_LIMIT_EXCEEDED;
	else if (normal_exit)
		return (exit_status == 0) ? EXIT_ALL_OK : EXIT_NONZERO_STATUS;
	else
		return EXIT_KILLED_BY_SIGNAL;
}

/* end */
