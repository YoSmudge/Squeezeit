"""
Squeezeit - Python CSS and Javascript minifier
Copyright (C) 2011 Sam Rudge

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import re
import hashlib
import logging
import yaml
import jsmin
import slimmer
import zlib

def compress(configfile):
	"""
	Do everything
	"""
	
	config = loadconfig(configfile)
	bundles = loadbundles(configfile, config)
	
	outputinfo = {}
	
	for bundle in bundles:
		logging.info("Processing {0}".format(bundle))
		bundleinfo = processbundle(configfile, config, bundle, bundles[bundle])
		
		outputinfo[bundle] = bundleinfo
	
	#Write the bundleinfo file
	infofile = os.path.abspath(os.path.join(
		os.getcwd(),
		os.path.dirname(configfile),
		config['output'],
		'info.yaml'
		))
	
	try:
		f = open(infofile, 'w')
		f.write(yaml.dump(outputinfo))
		f.close()
	except:
		logging.critical("Could not write infofile {0}".format(infofile))
		sys.exit(1)

def loadconfig(configfile):
	"""
	Load and parse the main configuration file
	"""
	
	#Load the bundle data
	configfile = os.path.join(os.getcwd(), configfile)
	
	try:
		f = open(configfile)
		configdata = f.read()
		f.close()
	except:
		logging.critical("Could not open bundle file {0}!".format(configfile))
		sys.exit(1)
	
	#PyYAML doesn't seem to like tabs used for spacing in YAML files, so replace them with 4 spaces
	configdata = configdata.replace("\t", "  ")
	
	#Parse the YAML into an array
	try:
		config = yaml.load(configdata)
	except:
		logging.critical("Could not parse YAML in {0}!".format(configfile))
		sys.exit(1)
	
	#Set the debug level
	try:
		logging.basicConfig(level=getattr(logging,config['logging'].upper()))
	except:
		logging.warning("Could not set logging level!")
	
	logging.info('Config loaded')
	
	return config

def loadbundles(configfile,config):
	"""
	Load the bundle data from the config files
	"""
	
	bundledir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(configfile), config['bundles']))
	
	logging.info('Loading bundle files from {0}'.format(bundledir))
	
	bundledata = {}
	
	#Get a list of files from the directory
	for file in os.listdir(bundledir):
		#Bundle files should be alpha-numeric files with a .yaml extension
		match = re.search(r"^([a-z0-9]+)\.yaml$", file)
		if match:
			logging.info("Found bundle {0}".format(file))
			
			#Load the bundle data
			try:
				f = open(os.path.join(bundledir,file))
				bundleraw = f.read()
				f.close()
			except:
				logging.critical("Could not read bundle file {0}".format(os.path.join(bundledir,file)))
				sys.exit(1)
			
			#Once again swap the tabs
			bundleraw = bundleraw.replace("\t", "  ")
			
			bundleconfig = yaml.load(bundleraw)
			
			bundledata[match.group(1)] = bundleconfig
	
	return bundledata

def loadfiles(configfile, config, srcdir, files):
	"""
	Load files from disk into a combined string
	"""
	
	srcdir = os.path.abspath(os.path.join(
		os.getcwd(),
		os.path.dirname(configfile),
		srcdir
		))
	
	rawdata = []
	
	for file in files:
		try:
			filepath = os.path.join(srcdir,file)
			f = open(filepath)
			filedata = f.read()
			f.close()
			
			rawdata.append(filedata)
		except:
			logging.warning("Could not read {0}". format(filepath))
	
	return ''.join(rawdata)

def writedata(configfile, config, output, filename, rawdata):
	"""Write the file data to the output directory"""
	
	outfile = os.path.abspath(os.path.join(
		os.getcwd(),
		os.path.dirname(configfile),
		config['output'],
		filename
		))
	
	try:
		f = open(outfile, 'w')
		f.write(rawdata)
		f.close()
	except:
		logging.critical("Could not write file {0}".format(outfile))
		sys.exit(1)

def processbundle(configfile, config, bundlename, bundledata):
	"""The interesting bit, load and process the bundle data"""
	
	#Make sure all items in the array are avaliable so as not to confuse upstream applications
	bundleinfo = {
		'css':{
			'md5':False,
			'size':{
				'raw':0,
				'min':0,
				'gz':0
			},
			'output':{
				'raw':False,
				'min':False,
				'gz':False
			},
			'files':[]
		},
		'javascript':{
			'md5':False,
			'size':{
				'raw':0,
				'min':0,
				'gz':0
			},
			'output':{
				'raw':False,
				'min':False,
				'gz':False
			},
			'files':[]
		}
	}
	
	#Javascript is processed first
	if bundledata['includes']['javascript']:
		logging.info('-Processing Javascript')
		rawdata = loadfiles(configfile, config, config['javascript'], bundledata['includes']['javascript'])
		
		#Some info
		md5 = hashlib.md5(rawdata).hexdigest()
		bundleinfo['javascript']['md5'] = md5
		bundleinfo['javascript']['files'] = bundledata['includes']['javascript']
		
		#Calculate the filename
		filename = {}
		
		if config['hashfilenames'] == True:
			filename['raw'] = '{0}-{1}.{2}'.format(bundlename, md5, 'js')
			filename['min'] = '{0}-{1}.{2}'.format(bundlename, md5, 'min.js')
			filename['gz'] = '{0}-{1}.{2}'.format(bundlename, md5, 'min.js.gz')
		else:
			filename['raw'] = '{0}.{1}'.format(bundlename, 'js')
			filename['min'] = '{0}.{1}'.format(bundlename, 'min.js')
			filename['gz'] = '{0}.{1}'.format(bundlename, 'min.js.gz')
		
		bundleinfo['javascript']['output'] = filename
		
		#Write the bundle file raw data
		writedata(configfile, config, config['output'], filename['raw'], rawdata)
		
		#Minify
		mindata = jsmin.jsmin(rawdata)
		writedata(configfile, config, config['output'], filename['min'], mindata)
		
		#Gzip
		gzdata = zlib.compress(mindata)
		writedata(configfile, config, config['output'], filename['gz'], gzdata)
		
		#Save the sizes
		bundleinfo['javascript']['size'] = {
			'raw':len(rawdata),
			'min':len(mindata),
			'gz':len(gzdata)
		}
		
	#Now CSS (same as above, but a little different)
	if bundledata['includes']['css']:
		logging.info('-Processing CSS')
		rawdata = loadfiles(configfile, config, config['css'], bundledata['includes']['css'])

		#Some info
		md5 = hashlib.md5(rawdata).hexdigest()
		bundleinfo['css']['md5'] = md5
		bundleinfo['css']['files'] = bundledata['includes']['css']

		#Calculate the filename
		filename = {}

		if config['hashfilenames'] == True:
			filename['raw'] = '{0}-{1}.{2}'.format(bundlename, md5, 'css')
			filename['min'] = '{0}-{1}.{2}'.format(bundlename, md5, 'min.css')
			filename['gz'] = '{0}-{1}.{2}'.format(bundlename, md5, 'min.css.gz')
		else:
			filename['raw'] = '{0}.{1}'.format(bundlename, 'css')
			filename['min'] = '{0}.{1}'.format(bundlename, 'min.css')
			filename['gz'] = '{0}.{1}'.format(bundlename, 'min.css.gz')

		bundleinfo['css']['output'] = filename

		#Write the bundle file raw data
		writedata(configfile, config, config['output'], filename['raw'], rawdata)

		#Minify
		mindata = slimmer.css_slimmer(rawdata)
		writedata(configfile, config, config['output'], filename['min'], mindata)

		#Gzip
		gzdata = zlib.compress(mindata)
		writedata(configfile, config, config['output'], filename['gz'], gzdata)

		#Save the sizes
		bundleinfo['css']['size'] = {
			'raw':len(rawdata),
			'min':len(mindata),
			'gz':len(gzdata)
		}

	
	return bundleinfo

