import pimped_subprocess
import logging

class _CaptureProcessID( object ):
    def __init__( self ):
        self.pid = None

    def __call__( self, line ):
        if self.pid is not None:
            return
        self.pid = int( line )


class Remote( object ):
    def __init__( self, user, host, command ):
        exposePidScript = self._exposePidScript( command )
        sshCommand = [ 'ssh', '{}@{}'.format( user, host ), '''bash -c "{}"'''.format( exposePidScript ) ]
        logging.info( 'running {}'.format( sshCommand ) )
        self._subProcess = pimped_subprocess.PimpedSubprocess( sshCommand )

    def _exposePidScript( self, command ):
        script = 'echo $$; exec {}'.format( command )
        return script

    def _launchProcess( self ):
        self._captureProcessId = _CaptureProcessID()
        self._subProcess.onOutput( self._captureProcessId )
        self._subProcess.launch()

    def foreground( self ):
        self._launchProcess()
        return self._subProcess.process.wait()

    @property
    def pid( self ):
        return self._captureProcessId.pid
