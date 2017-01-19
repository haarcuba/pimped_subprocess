import pimped_subprocess.pimped_subprocess_ as pimped_subprocess
import pytest
from testix.frequentlyused import *
import testix.saveargument
from testix import saveargument
import select as real_select

pimped_subprocess.subprocess = FakeObject( 'subprocess' )
pimped_subprocess.threading = FakeObject( 'threading' )
pimped_subprocess.pty = FakeObject( 'pty' )
pimped_subprocess.os = FakeObject( 'os' )
pimped_subprocess.select = FakeObject( 'select' )
pimped_subprocess.select.POLLIN = real_select.POLLIN
pimped_subprocess.select.POLLERR = real_select.POLLERR

class EndTestException( Exception ): pass

DEFAULT_TIMEOUT = 1000

class TestPimpedSubprocess:
    def construct( self, monitorFunction, popenArgs, popenKwargs ):
        with Scenario() as scenario:
            kwargExpectations = dict( popenKwargs )
            kwargExpectations.update( dict( stdout = FakeObject( 'writeDescriptor' ), close_fds = True ) )
            scenario <<\
                Call( 'pty.openpty', [], ( FakeObject( 'writeDescriptor' ), FakeObject( 'readDescriptor' ) ) ) <<\
                Call( 'subprocess.Popen', popenArgs, FakeObject( 'subProcess' ), kwargExpectations = kwargExpectations ) <<\
                Call( 'os.fdopen', [ FakeObject( 'readDescriptor' ), 'r' ], FakeObject( 'readStream' ) ) <<\
                Call( 'select.poll', [], FakeObject( 'poller' ) ) <<\
                Call( 'readStream.fileno', [], 'the_file_descriptor' ) <<\
                Call( 'poller.register', [ 'the_file_descriptor', real_select.POLLIN | real_select.POLLERR ], None ) <<\
                Call( 'threading.Thread', [], FakeObject( 'the_thread' ), kwargExpectations = { 'target': saveargument.SaveArgument( 'monitorThread' ) } ) <<\
                Call( 'the_thread.start', [], None )

            self.tested = pimped_subprocess.PimpedSubprocess( * popenArgs, ** popenKwargs )
            if monitorFunction is not None:
                self.tested.register( monitorFunction )
            self.tested.launch()
            assert FakeObject( 'the_thread' ).daemon == True

        self.monitorThread = saveargument.saved()[ 'monitorThread' ]

    def test_expose_process_api( self ):
        self.construct( None, [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        assert self.tested.process == FakeObject( 'subProcess' )
        
    def test_launch_process_no_monitor( self ):
        self.construct( None, [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        with Scenario() as scenario:
            scenario <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 1\n' ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 2\n' ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 3\n' ) <<\
                ThrowingCall( 'poller.poll', [ DEFAULT_TIMEOUT ], EndTestException )

            with pytest.raises( EndTestException ):
                self.monitorThread()

    def test_monitor_output_using_poll( self ):
        self.construct( FakeObject( 'monitorFunction' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        with Scenario() as scenario:
            scenario <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 1\n' ) <<\
                Call( 'monitorFunction', [ 'line 1' ], None ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 2\n' ) <<\
                Call( 'monitorFunction', [ 'line 2' ], None ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [] ) <<\
                Call( 'subProcess.poll', [], None ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [] ) <<\
                Call( 'subProcess.poll', [], None ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 3\n' ) <<\
                Call( 'monitorFunction', [ 'line 3' ], None ) <<\
                ThrowingCall( 'poller.poll', [ DEFAULT_TIMEOUT ], EndTestException )

            with pytest.raises( EndTestException ):
                self.monitorThread()

    def test_if_nothing_to_read_and_process_ended_cleanup_and_exit_thread( self ):
        self.construct( FakeObject( 'monitorFunction' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        with Scenario() as scenario:
            scenario <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [ ( 'file_descriptor', real_select.POLLIN ) ] ) <<\
                Call( 'readStream.readline', [], 'line 1\n' ) <<\
                Call( 'monitorFunction', [ 'line 1' ], None ) <<\
                Call( 'poller.poll', [ DEFAULT_TIMEOUT ], [] ) <<\
                Call( 'subProcess.poll', [], 0 ) <<\
                Call( 'readStream.close', [], None )

            self.monitorThread()
