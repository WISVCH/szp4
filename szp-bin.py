#!/usr/bin/python

from django.core.management import setup_environ
import settings

setup_environ(settings)

from cli import main

if __name__ == '__main__':
	main.main()
	
