import threading
import os
import pty
import subprocess

class PimpedSubprocess( object ):
    def __init__( self, * popenArgs, ** popenKwargs ):
        self._popenArgs = popenArgs
        self._popenKwargs = popenKwargs

    def launch( self ):
        write, read = pty.openpty()
        self._popenKwargs[ 'stdout' ] = write
        self._popenKwargs[ 'close_fds' ] = True
        self._subprocess = subprocess.Popen( * self._popenArgs, ** self._popenKwargs )
        self._reader = os.fdopen( read, 'r' )
        self._thread = threading.Thread( target = self._monitor )
        self._thread.daemon = True
        self._thread.start()

    def register( self, monitor ):
        pass

    def _monitor( self ):
        pass

