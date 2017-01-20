#!/usr/bin/python
import threading
import time
import argparse
import logging
import pimped_subprocess.remote

parser = argparse.ArgumentParser()
parser.add_argument( 'user' )
parser.add_argument( 'host' )
arguments = parser.parse_args()


logging.basicConfig( level = logging.INFO )


A_LONG_TIME = 1000
tested = pimped_subprocess.remote.Remote( arguments.user, arguments.host, "sleep {}".format( A_LONG_TIME ) )
tested.background( cleanup = True )
LET_PROCESS_RUN_A_LITTLE = 1
time.sleep( LET_PROCESS_RUN_A_LITTLE )
print( "remote process pid is {}. press key to end this and check that it died".format( tested.pid ) )
raw_input( "press key..." )
