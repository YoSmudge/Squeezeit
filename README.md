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

#WTF?
Squeezeit is a small Python utility to scratch my own personal itch. It attempts to provide a lot of the features of the Rails asset pipeline with regards to combining and minifying bundles of Javascript and CSS files, pre-compressing .gz versions of files and simplifying management of site media.

#Make shit happen
Download, `setup.py install` and run squeezeit `/path/to/config.yaml` (see below)

#Configuration
Squeezeit is configured through the use of YAML files. There are two types of YAML file needed for squeezeit to run;

##Main config.yaml
Specifies the main configuration options for the bundler, such as source directories and output directories.

	#Main bundle config
	#All paths are relative to this file

	#Logging level (Standard Python logging levels: DEBUG, INFO, WARNING or CRITICAL)
	logging: INFO

	#Specify the directory for bundle YAML files (The files that specify your bundles and their contents)
	bundles: ./config/

	#Where to output the bundles and bundle info file
	output: ./bundles/

	#Source files
	css: ./css/
	javascript: ./js/

	#Bundle names include MD5 hash of contents (E.G. [bundlename]-[md5 hash].js - See bundle info file)
	hashfilenames: true

##Bundle configuration files
These are YAML files in the 'bundles' directory specified above. A bundle config file contains all the media that should be included with a particular bundle. Output bundles will be named the same as the YAML file (so media.yaml will output media.js, media.css etc.)

	#Paths are relative to the 'source file' directories specified in the main config file
	includes:
	    css:
	        - clear.css
	        - fonts.css
	        - bootstrap.css
			- main.css
	    javascript:
	        - jquery/core.js #Oh, you can use sub-folders too
	        - main.js

All bundles will output 6 (or 3) files;

 * bundlename.js/css - Combined but not minified files, this is the same as `cat file1.js file2.js >> bundle.js`
 * bundlename.min.js/css - Combined and minified versions of the files. JS minification is done using JSMin and CSS minification is done using slimmer
 * bundlename.min.js/css.gz - Combined, minified and GZipped version of the file.

You don't have to include both javascript and CSS in a bundle, just leave the array blank in the bundle config file

##Bundle info file
The bundler outputs a 'bundle info file' to output-directory/info.yaml. The bundle info file contains information about the sizes of the bundles, and their MD5 has (useful for using MD5 in filenames).

	media:
		css:
			md5: 3c716f5993efd3257fe17b219c6b6ecd #MD5 is generated from the combined data, before it's minified
			output: {
				gz: media-3c716f5993efd3257fe17b219c6b6ecd.min.css.gz,
				min: media-3c716f5993efd3257fe17b219c6b6ecd.min.css,
				raw: media-3c716f5993efd3257fe17b219c6b6ecd.css
			}
			size: {
				gz: 328,
				min: 704,
				raw: 821
			}
		javascript:
			md5: 9581d699b54badf07d4e1f60f77dca7d
			output: {
				gz: media-9581d699b54badf07d4e1f60f77dca7d.min.js.gz,
				min: media-9581d699b54badf07d4e1f60f77dca7d.min.js,
				raw: media-9581d699b54badf07d4e1f60f77dca7d.js
			}
			size: {
				gz: 33142,
				min: 93837,
				raw: 93939
			}

If ether Javascript or CSS source files are not specified in the bundle, the value of 'md5' will be set to false (`md5: false`) so you can detect that from your code.

#It wasn't all me

Squeezeit includes two excellent libraries to do it's work (on top of the standard Python ones);

 * JSMin.py - By Douglas Crockford and Dave St.Germain
 * Slimmer - By Peter Bengtsson

Other cool things to check out;

 * [PNGCrush](http://pmt.sourceforge.net/pngcrush/) - Great at optimising images and stuff