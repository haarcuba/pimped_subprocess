import pimped_subprocess
import time

class PrependLineNumber( object ):
    def __init__( self ):
        self._counter = 0

    def __call__( self, line ):
        self._counter += 1
        print( '{:04}:\t{}'.format( self._counter, line ) )

prependLineNumber = PrependLineNumber()
p = pimped_subprocess.PimpedSubprocess( 'ls -l', shell = True )

# must register to get the lines
p.onOutput( prependLineNumber )

# acutally run the subprocess
p.launch()

# wait for it to finish
p.process.wait()
time.sleep( 0.1 ) # wait a little extra to finish reading everything