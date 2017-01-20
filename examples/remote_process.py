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


processDone = threading.Event()
tested = pimped_subprocess.remote.Remote( arguments.user, arguments.host, "bash -c 'sleep 10 ; exit 55'" )

def onDeath( token, exitCode ):
    global processDone
    logging.info( 'process done: {}'.format( ( token, exitCode ) ) )
    processDone.set()

tested.subProcess.onProcessEnd( onDeath, 'my token' )
tested.background()
time.sleep( 1 )
print( 'remote process pid is {}'.format( tested.pid ) )

processDone.wait()
