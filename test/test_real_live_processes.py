import pimped_subprocess

class Accumulate( object ):
    def __init__( self ):
        self.lines = []

    def __call__( self, line ):
        self.lines.append( line )

class TestActual( object ):
    def test_ls( self ):
        tested = pimped_subprocess.PimpedSubprocess( 'ls -l test/fixtures/*', shell = True )
        accumulate = Accumulate()
        tested.register( accumulate )
        tested.launch()
        tested.process.wait()
        actualFilenames = set( line.split()[ -1 ] for line in accumulate.lines )
        assert actualFilenames == set( [ 'test/fixtures/one', 'test/fixtures/two', 'test/fixtures/three' ] )
