# Pimped Subprocess

`PimpedSubprocess` allows you to run subprocesses in a similar manner to Python's standard `subprocesses`, except that it allows you to follow the subprocess `stdout` stream line by line.

```python
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
```

This code will produce something like this:

    0001:   total 44
    0002:   drwxrwxr-x 2 yoav yoav 4096 ינו 19 02:40 dist
    0003:   drwxrwxr-x 2 yoav yoav 4096 ינו 19 02:52 examples
    0004:   -rw-rw-r-- 1 yoav yoav  258 ינו 19 02:35 go.py
    0005:   drwxrwxr-x 2 yoav yoav 4096 ינו 19 02:39 pimped_subprocess
    0006:   drwxrwxr-x 2 yoav yoav 4096 ינו 18 23:58 pimped_subprocess.egg-info
    0007:   drwxrwxr-x 7 yoav yoav 4096 ינו 19 00:38 python2
    0008:   -rw-rw-r-- 1 yoav yoav  230 ינו 19 01:28 Rakefile
    0009:   -rw-rw-r-- 1 yoav yoav  922 ינו 19 02:54 README.md
    0010:   -rw-rw-r-- 1 yoav yoav  700 ינו 19 02:40 setup.py
    0011:   drwxrwxr-x 4 yoav yoav 4096 ינו 19 02:34 test
    0012:   drwxrwxr-x 2 yoav yoav 4096 ינו 19 01:41 tools


# Multiple Output Monitors

You can register multiple output monitors by calling `onOutput` multiple times:

```python
p.onOutput( callable1 )
p.onOutput( callable2 )
p.onOutput( callable3 )
```

# Process End Event

You can also register to get notified when the process ends:

```python

def myCallback( token, exitCode ):
    print( 'process ended with exit code: {}'.format( exitCode ) )

p.onProcessEnd( myCallback, 'some token here' )
```

When the process ends, `myCallback` will be called with the token and the process's exit code.
The token's job is to help you distinguish between different processes that use the same callback.
