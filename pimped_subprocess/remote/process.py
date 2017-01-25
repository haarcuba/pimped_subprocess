import atexit
import pimped_subprocess

class _CaptureProcessID( object ):
    def __init__( self ):
        self.pid = None

    def __call__( self, line ):
        if self.pid is not None:
            return
        self.pid = int( line )


class Process( object ):
    def __init__( self, user, host, command ):
        exposePidScript = self._exposePidScript( command )
        self._user = user
        self._host = host
        sshCommand = [ 'ssh', '{}@{}'.format( user, host ), '''bash -c "{}"'''.format( exposePidScript ) ]
        self._subProcess = pimped_subprocess.PimpedSubprocess( sshCommand )
        self._captureProcessId = _CaptureProcessID()
        self._subProcess.onOutput( self._captureProcessId )

    def _exposePidScript( self, command ):
        script = 'echo $$; exec {}'.format( command )
        return script

    def foreground( self ):
        self._subProcess.launch()
        return self._subProcess.process.wait()

    def background( self, cleanup = False ):
        if cleanup:
            atexit.register( self._killRemote )
        self._subProcess.launch()

    def _killRemote( self ):
        sshCommand = [ 'ssh', '{}@{}'.format( self._user, self._host ), 'kill', str( self.pid ) ]
        killer = pimped_subprocess.PimpedSubprocess( sshCommand )
        killer.launch()
        return killer.process.wait()

    @property
    def subProcess( self ):
        return self._subProcess

    @property
    def pid( self ):
        return self._captureProcessId.pid
