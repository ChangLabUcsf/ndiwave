# ndiwave
Utilities for working with the NDI Wave motion capture system.

## Install

Clone the repository:

    git clone https://github.com/rsprouse/ndiwave

Run setup:

    cd ndiwave
    python setup.py install

## Example

    from ndiwave.controller import NDIWaveController

    # Connect to RT Server on localhost (default), port 3030 (default).
    # Use the `address` and `port` parameters of NDIWaveController()
    # for non-default IP address or port.
    c = NDIWaveController()
    c.connect()

    for fname in ['test1.csv', 'test2.csv']:
        # Record for 30 seconds into a file named fname.
        c.start_rec(fname, dur=30, units='seconds')
        # Probably need to wait for dur here, or possibly poll the
        # server to determine if it is still recording.

    for fname in ['vartest1.csv', 'vartest2.csv']:
        # Record for variable length into a file named fname.
        c.start_rec(fname)
        # Do something for a while.
        c.stop_rec()

    # Say goodbye to the server and close the socket.
    c.close()


