import pimped_subprocess

class AddLineCounter( object ):
    def __init__( self ):
        self._counter = 0

    def __call__( self, line ):
        self._counter += 1
        print( '{:04}:\t{}'.format( self._counter, line ) )

addLineCounter = AddLineCounter()
p = pimped_subprocess.PimpedSubprocess( 'ls -l', shell = True )

# must register to get the lines
p.register( addLineCounter )

# acutally run the subprocess
p.launch()

# wait for it to finish
p.process.wait()
