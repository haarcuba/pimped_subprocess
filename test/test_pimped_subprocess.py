import pimped_subprocess.pimped_subprocess_ as pimped_subprocess
import pytest
from testix.frequentlyused import *
from testix import patch_module
import testix.saveargument
from testix import saveargument
import select as real_select


class EndTestException( Exception ): pass

DEFAULT_TIMEOUT = 1000

class TestPimpedSubprocess:
    def construct( self, monitorFunction, popenArgs, popenKwargs ):
        with Scenario() as s:
            kwargExpectations = dict( popenKwargs )
            kwargExpectations.update( dict( stdout = FakeObject( 'writeDescriptor' ), close_fds = True ) )

            s.pty.openpty()                                                     >> ( FakeObject( 'writeDescriptor' ), FakeObject( 'readDescriptor' ) )
            s.subprocess.Popen( * popenArgs, ** kwargExpectations )             >> FakeObject( 'subProcess' )
            s.open( FakeObject( 'readDescriptor' ), 'r', encoding = 'latin-1' ) >> FakeObject( 'readStream' )
            s.select.poll()                                                     >> FakeObject( 'poller' )
            s.readStream.fileno()                                               >> 'the_file_descriptor'
            s.poller.register( 'the_file_descriptor', real_select.POLLIN | real_select.POLLERR )
            s.threading.Thread( target = saveargument.SaveArgument( 'monitorThread' ) )\
                                                                                >> FakeObject( 'the_thread' )
            s.the_thread.start()

            self.tested = pimped_subprocess.PimpedSubprocess( * popenArgs, ** popenKwargs )
            if monitorFunction is not None:
                self.tested.onOutput( monitorFunction )
            self.tested.launch()
            assert FakeObject( 'the_thread' ).daemon == True

        self.monitorThread = saveargument.saved()[ 'monitorThread' ]

    @pytest.fixture
    def module_patch( self, patch_module ):
        patch_module( pimped_subprocess, 'subprocess' )
        patch_module( pimped_subprocess, 'threading' )
        patch_module( pimped_subprocess, 'pty' )
        patch_module( pimped_subprocess, 'open' )
        fakeSelect = patch_module( pimped_subprocess, 'select' )
        fakeSelect.POLLIN = real_select.POLLIN
        fakeSelect.POLLERR = real_select.POLLERR

    def test_construct( self, module_patch ):
        self.construct( None, [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )

    def test_expose_process_api( self, module_patch ):
        self.construct( None, [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        assert self.tested.process == FakeObject( 'subProcess' )

    def test_launch_process_no_monitor( self, module_patch ):
        self.construct( None, [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        with Scenario() as s:
            s.poller.poll( DEFAULT_TIMEOUT )            >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline()                     >> 'line 1\n'
            s.poller.poll( DEFAULT_TIMEOUT )            >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline()                     >> 'line 2\n'
            s.poller.poll( DEFAULT_TIMEOUT )            >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline()                     >> 'line 3\n'
            s.poller.poll( DEFAULT_TIMEOUT ).throwing( EndTestException )

            with pytest.raises( EndTestException ):
                self.monitorThread()

    def test_monitor_output_using_poll( self, module_patch ):
        self.construct( FakeObject( 'monitorFunction' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        with Scenario() as s:
            s.poller.poll( DEFAULT_TIMEOUT )    >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline()             >> 'line 1\n'
            s.monitorFunction( 'line 1' )
            s.poller.poll( DEFAULT_TIMEOUT ) >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline() >> 'line 2\n'
            s.monitorFunction( 'line 2' )
            s.poller.poll( DEFAULT_TIMEOUT ) >> []
            s.subProcess.poll()
            s.poller.poll( DEFAULT_TIMEOUT ) >> []
            s.subProcess.poll()
            s.poller.poll( DEFAULT_TIMEOUT ) >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline() >> 'line 3\n'
            s.monitorFunction( 'line 3' )
            s.poller.poll( DEFAULT_TIMEOUT ).throwing( EndTestException )

            with pytest.raises( EndTestException ):
                self.monitorThread()

    def test_register_multiple_monitors( self, module_patch ):
        self.construct( FakeObject( 'monitorFunction1' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        self.tested.onOutput( FakeObject( 'monitorFunction2' ) )
        self.tested.onOutput( FakeObject( 'monitorFunction3' ) )
        with Scenario() as s:
            s.poller.poll( DEFAULT_TIMEOUT ) >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline() >> 'line 1\n'
            s.monitorFunction1( 'line 1' )
            s.monitorFunction2( 'line 1' )
            s.monitorFunction3( 'line 1' )
            s.poller.poll( DEFAULT_TIMEOUT ) >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline() >> 'line 2\n'
            s.monitorFunction1( 'line 2' )
            s.monitorFunction2( 'line 2' )
            s.monitorFunction3( 'line 2' )
            s.poller.poll( DEFAULT_TIMEOUT ).throwing( EndTestException )

            with pytest.raises( EndTestException ):
                self.monitorThread()

    def test_if_nothing_to_read_and_process_ended_cleanup_and_exit_thread( self, module_patch ):
        self.construct( FakeObject( 'monitorFunction' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        with Scenario() as s:
            s.poller.poll( DEFAULT_TIMEOUT ) >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline() >> 'line 1\n'
            s.monitorFunction( 'line 1' ) >> None
            s.poller.poll( DEFAULT_TIMEOUT ) >> []
            s.subProcess.poll() >> 0
            s.readStream.close() 

            self.monitorThread()

    def test_inform_about_process_death_via_callback( self, module_patch ):
        self.construct( FakeObject( 'monitorFunction' ), [ 'popen', 'arguments' ], { 'some': 'kwargs', 'for': 'Popen' } )
        self.tested.onProcessEnd( FakeObject( 'myEndCallback' ) )
        with Scenario() as s:
            s.poller.poll( DEFAULT_TIMEOUT ) >> [ ( 'file_descriptor', real_select.POLLIN ) ]
            s.readStream.readline() >> 'line 1\n'
            s.monitorFunction( 'line 1' ) >> None
            s.poller.poll( DEFAULT_TIMEOUT ) >> []
            s.subProcess.poll() >> 255
            s.readStream.close()
            s.myEndCallback( 255 )

            self.monitorThread()
