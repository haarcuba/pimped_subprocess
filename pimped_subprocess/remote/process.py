import atexit
import os
import pimped_subprocess
import subprocess
import logging
import pimped_subprocess.remote.temporary_folder
import tempfile
from pimped_subprocess import remote

class _CaptureProcessID( object ):
    def __init__( self ):
        self.pid = None

    def __call__( self, line ):
        if self.pid is not None:
            return
        self.pid = int( line )

_RUNNER_TEMPLATE = \
"""#!/bin/bash
echo $$
exec {}
"""

class Process( object ):
    def __init__( self, user, host, script ):
        self._user = user
        self._host = host
        self._script = script
        self._remoteFolder = remote.temporary_folder.temporaryFolder( self._user, self._host )
        self._remoteClientScript = self._prepareRemoteScript( script, 'client.sh' )
        self._remoteRunnerScript = self._prepareRemoteScript( _RUNNER_TEMPLATE.format( self._remoteClientScript ), 'runner.sh' )
        sshCommand = [ 'ssh', '{}@{}'.format( user, host ), self._remoteRunnerScript ]
        self._subProcess = pimped_subprocess.PimpedSubprocess( sshCommand )
        self._captureProcessId = _CaptureProcessID()
        self._subProcess.onOutput( self._captureProcessId )

    def _copyToRemote( self, source, destination ):
        scpTarget = '{user}@{host}:{path}'.format( user = self._user, host = self._host, path = destination )
        logging.info( str( [ 'scp', '-p', source, scpTarget ] ) )
        subprocess.check_call( [ 'scp', '-p', source, scpTarget ] )

    def _prepareRemoteScript( self, content, filename ):
        localScript = tempfile.NamedTemporaryFile()
        os.chmod( localScript.name, 0777 )
        with open( localScript.name, 'w' ) as f:
            f.write( content )

        remoteScript = '{}/{}'.format( self._remoteFolder, filename )
        self._copyToRemote( localScript.name, remoteScript )
        return remoteScript

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
