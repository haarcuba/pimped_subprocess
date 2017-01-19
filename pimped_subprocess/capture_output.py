class CaptureOutput( object ):
    def __init__( self ):
        self._lines = []

    def __call__( self, line ):
        self._lines.append( line )

    @property
    def lines( self ):
        return self._lines

    @property
    def text( self ):
        return '\n'.join( self._lines )
