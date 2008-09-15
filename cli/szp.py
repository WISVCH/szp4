#!/usr/bin/python

import os
import sys

# This will insert the parent duriectory to the path so we can import
# settings.
sys.path.insert(0, os.path.normpath(sys.path[0]+"/.."))

from django.core.management import setup_environ
import settings

setup_environ(settings)

import main

if __name__ == '__main__':
	main.main()
	
