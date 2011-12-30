#!/usr/bin/env python
 
from setuptools import setup, find_packages
import sys, os
 
version = '0.7'
 
setup(name='squeezeit',
	version=version,
	author='Sam Rudge',
	author_email='sam@rmg.io',
	packages=['squeezeit'],
	include_package_data=True,
	zip_safe=False,
	entry_points="""
	[console_scripts]
	squeezeit = squeezeit.cli:start
	""",
	install_requires=[
		'pyyaml=>3.10'
	]
	)