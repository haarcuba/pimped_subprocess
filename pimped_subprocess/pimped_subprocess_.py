import threading
import os
import pty
import subprocess
import select

class PimpedSubprocess( object ):
    def __init__( self, * popenArgs, ** popenKwargs ):
        self._popenArgs = popenArgs
        self._popenKwargs = popenKwargs
        self._outputMonitors = []
        self._onProcessEnd = None

    def launch( self ):
        write, read = pty.openpty()
        self._popenKwargs[ 'stdout' ] = write
        self._popenKwargs[ 'close_fds' ] = True
        self._subprocess = subprocess.Popen( * self._popenArgs, ** self._popenKwargs )
        self._reader = os.fdopen( read, 'r' )
        self._poller = select.poll()
        self._poller.register( self._reader.fileno(), select.POLLIN | select.POLLERR )
        self._thread = threading.Thread( target = self._monitorProcess )
        self._thread.daemon = True
        self._thread.start()

    def register( self, monitor ):
        self._outputMonitors.append( monitor )

    @property
    def process( self ):
        return self._subprocess

    def _monitorProcess( self ):
        TIMEOUT_MILLISECONDS = 1000
        while True:
            events = self._poller.poll( TIMEOUT_MILLISECONDS )
            if not self._readable( events ):
                exitCode = self._subprocess.poll()
                if exitCode is not None:
                    self._processOver( exitCode )
                    return
                continue
            line = self._reader.readline()
            self._diseminate( line )

    def _diseminate( self, line ):
        for client in self._outputMonitors:
            client( line.strip() )

    def _readable( self, events ):
        for descriptor, event in events:
            if event & select.POLLIN:
                return True

        return False

    def onProcessEnd( self, callback, token ):
        self._onProcessEnd = dict( callback = callback, token = token )

    def _processOver( self, exitCode ):
        self._reader.close()
        if self._onProcessEnd is not None:
            self._onProcessEnd[ 'callback' ]( self._onProcessEnd[ 'token' ], exitCode )
