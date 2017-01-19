from pimped_subprocess import capture_output
import pimped_subprocess.pimped_subprocess_ as pimped_subprocess

class TestActual( object ):
    def test_ls( self ):
        tested = pimped_subprocess.PimpedSubprocess( 'ls -l test/fixtures/*', shell = True )
        capture = capture_output.CaptureOutput()
        tested.register( capture )
        tested.launch()
        tested.process.wait()
        actualFilenames = set( line.split()[ -1 ] for line in capture.lines )
        assert actualFilenames == set( [ 'test/fixtures/one', 'test/fixtures/two', 'test/fixtures/three' ] )
