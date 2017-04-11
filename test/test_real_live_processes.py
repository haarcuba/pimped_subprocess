from pimped_subprocess import capture_output
import pimped_subprocess.pimped_subprocess_ as pimped_subprocess
import time

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
        def _callback( exitCode ):
            endingParameters.append( exitCode )

        tested = pimped_subprocess.PimpedSubprocess( 'exit 77', shell = True )
        tested.onProcessEnd( _callback )
        tested.launch()
        tested.process.wait()
        time.sleep( 1.5 )
        assert endingParameters == [ 77 ]
