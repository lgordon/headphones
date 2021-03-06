#!/usr/bin/env python
import os, sys

from lib.configobj import ConfigObj

import headphones

from headphones import webstart, logger

try:
    import argparse
except ImportError:
    import lib.argparse as argparse
    

def main():

    # Fixed paths to Headphones
    if hasattr(sys, 'frozen'):
        headphones.FULL_PATH = os.path.abspath(sys.executable)
    else:
        headphones.FULL_PATH = os.path.abspath(__file__)
    
    headphones.PROG_DIR = os.path.dirname(headphones.FULL_PATH)
    headphones.ARGS = sys.argv[1:]
    
    # Set up and gather command line arguments
    parser = argparse.ArgumentParser(description='Music add-on for SABnzbd+')

    parser.add_argument('-q', '--quiet', action='store_true', help='Turn off console logging')
    parser.add_argument('-d', '--daemon', action='store_true', help='Run as a daemon')
    parser.add_argument('-p', '--port', type=int, help='Force Headphones to run on a specified port')
    parser.add_argument('--datadir', help='Specify a directory where to store your data files')
    parser.add_argument('--config', help='Specify a config file to use')
    parser.add_argument('--nolaunch', action='store_true', help='Prevent browser from launching on startup')
    
    args = parser.parse_args()
    
    if args.quiet:
        headphones.QUIET=True
    
    if args.daemon:
        headphones.DAEMON=True
        headphones.QUIET=True
        
    if args.datadir:
        headphones.DATA_DIR = args.datadir
    else:
        headphones.DATA_DIR = headphones.PROG_DIR
            
    if args.config:
        headphones.CONFIG_FILE = args.config
    else:
        headphones.CONFIG_FILE = os.path.join(headphones.DATA_DIR, 'config.ini')
        
    # Try to create the DATA_DIR if it doesn't exist
    if not os.path.exists(headphones.DATA_DIR):
        try:
            os.makedirs(headphones.DATA_DIR)
        except OSError:
            raise SystemExit('Could not create data directory: ' + headphones.DATA_DIR + '. Exiting....')
    
    # Make sure the DATA_DIR is writeable
    if not os.access(headphones.DATA_DIR, os.W_OK):
        raise SystemExit('Cannot write to the data directory: ' + headphones.DATA_DIR + '. Exiting...')
    
    # Put the database in the DATA_DIR
    headphones.DB_FILE = os.path.join(headphones.DATA_DIR, 'headphones.db')
    
    headphones.CFG = ConfigObj(headphones.CONFIG_FILE)
    
    # Read config & start logging
    headphones.initialize()
        
    if headphones.DAEMON:
        headphones.daemonize()
        
    # Force the http port if neccessary
    if args.port:
        http_port = args.port
        logger.info('Starting Headphones on foced port: %i' % http_port)
    else:
        http_port = int(headphones.HTTP_PORT)
        
    # Try to start the server. 
    webstart.initialize({
                    'http_port':        http_port,
                    'http_host':        headphones.HTTP_HOST,
                    'http_root':        headphones.HTTP_ROOT,
                    'http_username':    headphones.HTTP_USERNAME,
                    'http_password':    headphones.HTTP_PASSWORD,
            })
    
    logger.info('Starting Headphones on port: %i' % http_port)
    
    if headphones.LAUNCH_BROWSER and not args.nolaunch:
        headphones.launch_browser(headphones.HTTP_HOST, http_port, headphones.HTTP_ROOT)
        
    # Start the background threads
    headphones.start()
    
    return

if __name__ == "__main__":
    main()
