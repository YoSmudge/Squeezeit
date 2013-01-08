"""
Squeezeit can be run from the command line using the 'squeezeit' command
"""

import squeezeit

def start():
    """
    Start processing from the command line
    
    Loads the path to the config (from the argument variables) and runs the minification process
    
    run with
    squeezeit [relative path to bundle config file]
    """
    
    #Confirm the command line arguments exist
    if len(squeezeit.sys.argv) <= 1:
        squeezeit.logging.critical("Pass the location of the bundle file. See readme")
        squeezeit.sys.exit(1)
    
    bundleconfig = squeezeit.sys.argv[1]
    
    #Start the processing (Yes that's about it for this file)
    squeezeit.compress(bundleconfig)