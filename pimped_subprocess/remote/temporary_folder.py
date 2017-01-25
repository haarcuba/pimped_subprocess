import subprocess
import atexit

class TemporaryFolder( object ):
    def __init__( self, user, host ):
        self._user = user
        self._host = host
        self._path = subprocess.check_output( [ 'ssh', '{}@{}'.format( user, host ), 'mktemp -d' ] ).strip()
        atexit.register( self._cleanup )

    @property
    def path( self ):
        return self._path

    def _cleanup( self ):
        subprocess.call( [ 'ssh', '{}@{}'.format( self._user, self._host ), 'rm -fr {}'.format( self._path ) ] )

def temporaryFolder( user, host ):
    return TemporaryFolder( user, host ).path
