from pimped_subprocess import capture_output
import pimped_subprocess.pimped_subprocess_ as pimped_subprocess
import time
import pimped_subprocess.remote.process
from pimped_subprocess import remote

class TestRealLiveProcesses( object ):
    def test_ls( self ):
        tested = pimped_subprocess.PimpedSubprocess( 'ls -l test/fixtures/*', shell = True )
        capture = capture_output.CaptureOutput()
        tested.onOutput( capture )
        tested.launch()
        tested.process.wait()
        actualFilenames = set( line.split()[ -1 ] for line in capture.lines )
        assert actualFilenames == set( [ 'test/fixtures/one', 'test/fixtures/two', 'test/fixtures/three' ] )

    def test_inform_about_death_via_callback( self ):
        endingParameters = []
        def _callback( token, exitCode ):
            endingParameters.append( ( token, exitCode ) )

        tested = pimped_subprocess.PimpedSubprocess( 'exit 77', shell = True )
        tested.onProcessEnd( _callback, 'abcde_7' )
        tested.launch()
        tested.process.wait()
        time.sleep( 1.5 )
        assert len( endingParameters ) == 1
        assert endingParameters[ 0 ] == ( 'abcde_7', 77 )

    def test_run_ls_in_vagrant_via_ssh( self ):
        ip = '10.50.50.11'
        user = 'vagrant'
        tested = remote.process.Process( user, ip, "bash -c 'exit 77'" )
        exitCode = tested.foreground()
        assert exitCode == 77
