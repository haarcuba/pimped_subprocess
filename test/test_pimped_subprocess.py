import pimped_subprocess
from testix.frequentlyused import *
import testix.saveargument
from testix import saveargument

pimped_subprocess.subprocess = FakeObject( 'subprocess' )
pimped_subprocess.threading = FakeObject( 'threading' )
pimped_subprocess.pty = FakeObject( 'pty' )
pimped_subprocess.os = FakeObject( 'os' )

class TestPimpedSubprocess:
    def construct( self, monitorFunction, popenArgs, popenKwargs ):
        with Scenario() as scenario:
            kwargExpectations = dict( popenKwargs )
            kwargExpectations.update( dict( stdout = FakeObject( 'writeDescriptor' ), close_fds = True ) )
            scenario <<\
                Call( 'pty.openpty', [], ( FakeObject( 'writeDescriptor' ), FakeObject( 'readDescriptor' ) ) ) <<\
                Call( 'subprocess.Popen', popenArgs, FakeObject( 'popen' ), kwargExpectations = kwargExpectations ) <<\
                Call( 'os.fdopen', [ FakeObject( 'readDescriptor' ), 'r' ], FakeObject( 'readStream' ) ) <<\
                Call( 'threading.Thread', [], FakeObject( 'the_thread' ), kwargExpectations = { 'target': saveargument.SaveArgument( 'monitorThread' ) } ) <<\
                Call( 'the_thread.start', [], None )

            self.tested = pimped_subprocess.PimpedSubprocess( * popenArgs, ** popenKwargs )
            self.tested.register( monitorFunction )
            self.tested.launch()
            assert FakeObject( 'the_thread' ).daemon == True

        self.monitorThread = saveargument.saved()[ 'monitorThread' ]
        
    def test_launch_process( self ):
        self.construct( FakeObject( 'monitor' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
