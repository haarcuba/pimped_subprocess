import pimped_subprocess.remote
import pimped_subprocess.remote.process
from pimped_subprocess import remote
import pytest
from testix.frequentlyused import *
import testix.saveargument
from testix import saveargument

remote.process.pimped_subprocess = FakeObject( 'pimped_subprocess' )
remote.process.atexit = FakeObject( 'atexit' )
remote.process.pimped_subprocess.remote = FakeObject( 'remote' )
remote.process.subprocess = FakeObject( 'subprocess' )

class TestRemote( object ):
    def construct( self, user, host, command ):
        with Scenario() as scenario:
            sshCommand = [ 'ssh', '{}@{}'.format( user, host ), 'bash -c "echo $$; exec {}"'.format( command ) ]
            scenario <<\
                Call( 'pimped_subprocess.PimpedSubprocess', [ sshCommand ], FakeObject( 'pimpedSubprocess' ) ) <<\
                Call( 'pimpedSubprocess.onOutput', [ saveargument.SaveArgument( 'onOutputCallback' ) ], None )
            self.tested = remote.process.Process( user, host, command )
            self.onOutputCallback = saveargument.saved()[ 'onOutputCallback' ]

    def test_launch_process_in_foreground_via_ssh_and_detect_remote_pid( self ):
        self.construct( 'myuser', 'myhost', 'ls -l' )
        with Scenario() as scenario:
            scenario <<\
                Call( 'pimpedSubprocess.launch', [], None ) <<\
                Call( 'pimpedSubprocess.process.wait', [], 0 )
            self.tested.foreground()
            self.onOutputCallback( '6667' )
            self.onOutputCallback( 'line 1' )
            self.onOutputCallback( 'line 2' )
            assert self.tested.pid == 6667

    def test_launch_process_in_background_via_ssh_and_detect_remote_pid( self ):
        self.construct( 'myuser', 'myhost', 'ls -l' )
        with Scenario() as scenario:
            scenario <<\
                Call( 'pimpedSubprocess.launch', [], None )
            self.tested.background()
            self.onOutputCallback( '6667' )
            self.onOutputCallback( 'line 1' )
            self.onOutputCallback( 'line 2' )
            assert self.tested.pid == 6667

    def test_background_process_automatic_cleanup( self ):
        self.construct( 'myuser', 'myhost', 'sleep 1000' )
        with Scenario() as scenario:
            scenario <<\
                Call( 'atexit.register', [ saveargument.SaveArgument( 'atExitCallback' ) ], None ) <<\
                Call( 'pimpedSubprocess.launch', [], None )
            self.tested.background( cleanup = True )
            self.onOutputCallback( '6667' )
            self.onOutputCallback( 'line 1' )
            self.onOutputCallback( 'line 2' )
            assert self.tested.pid == 6667
            killerSSHCommand = [ 'ssh', '{}@{}'.format( 'myuser', 'myhost' ), 'kill', '6667' ]
            scenario <<\
                Call( 'pimped_subprocess.PimpedSubprocess', [ killerSSHCommand ], FakeObject( 'killer' ) ) <<\
                Call( 'killer.launch', [], None ) <<\
                Call( 'killer.process.wait', [], 0 )
            atExitCallback = saveargument.saved()[ 'atExitCallback' ]
            atExitCallback()
