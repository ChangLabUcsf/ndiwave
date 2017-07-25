import socket
import struct
import time

# NDIWave protocol
# A packet consists of:
#
# Bytes    Name    Description
# -------------------------
# 4        Size    the total size of packet, including the 4 bytes denoting size
# 4        Type    the type of data in the packet
# Size-8   Data    the packet data
#
# I.e. a packet's size is the data size + 8 (4+4) bytes of header.
#
# Notes:
#
# Packet headers are always big endian.
#
# Command strings are Type 1 and must be single-byte ASCII. Byte order is irrelevant.
# 
# Command strings allow but do not require null termination.
#

# Data types used in packet headers.
dtypes = {
    'error': 0,       # Error
    'string': 1,      # Commandstring or Command succeeed
    'xml': 2,         # XML
    'dataframe': 3,   # Data Frame
    'nodata': 4,      # No Data
    'c3dfile': 5      # Complete C3D file
}

class NDIWaveControllerError(Exception):
    pass

class NDIWaveController:
    '''Client controller for a running NDIWave server.'''
    def __init__(self, address='127.0.0.1', port=3030, buffer_size=8192):
        self.address = address
        self.port = port
        self.buffer_size = buffer_size
# TODO: what is appropriate buffer size?
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __repr__(self):
        '''String representation of the NDIWaveController object.'''
        return "NDIWaveController( address: {}, port: {:d}, buffer_size: {:d} )".format(
            self.address, self.port, self.buffer_size
        )

    def connect(self, timeout=5):
        '''Connect to the running NDIWave server. Give up after a period defined by timeout (in seconds).'''
        t_end = time.time() + timeout
        while True:
            try:
                self.socket.connect((self.address, self.port))
                break
            except Exception as e:
                if time.time() > t_end:
                    raise NDIWaveControllerError(
                        "Timeout while connecting to NDIWave server."
                    )

    def close(self):
        '''Close connecton to the NDIWave server.'''
        self.send_cmd('Bye')
        self.socket.close()

    def send_cmd(self, cmd):
        '''Send a command message to the NDIWave server.'''
# TODO: is there an acknowledgment to process? Error checking?
# TODO: should we bother with allowing cmd to already be a byte array?
        buff = cmd.encode('ascii')  # Convert string to byte array.
        pktsize = 4 + 4 + len(buff)
        fmt = '>II{}s'.format(len(buff))
        s = struct.Struct(fmt)
        packed_data = s.pack(pktsize, dtypes['string'], buff) 
        self.socket.send(packed_data)

    def receive(self, buffer_size=None):
        '''Receive data from the NDIWave server.'''
# TODO: Figure out how server sends messages back to the client.
        buffer_size = buffer_size or self.buffer_size
        data = self.socket.recv(buffer_size)
        hdfmt = '>II'
        s = struct.Struct(hdfmt)
        try:
            header = s.unpack(data[:8])
            msgsize = header[0]
            msgtype = header[1]
        except IndexError:
            raise RuntimeError('Could not unpack message header. Not enough data.')
        try:
            assert(len(data) == msgsize)
        except AssertionError:
            raise RuntimeError('Could not unpack message packet. Wrong number of bytes.')
        return data[8:], msgsize, msgtype

    def start_rec(self, fname=None, dur=None, units=None):
        '''Send a command to the NDIWave server to start recording.
fname = an ASCII string indicating the output filename
dur = duration to record; if not included or 0, recording will continue until Stop is received.
  Note: the NDIWave manual does not specify whether the duration must be an integer.
  The example it provides uses an integer, and we assume it will be an integer.
units = units used to interpret duration; must be 'seconds' or 'frames'
'''
        params = ['Start']
        if fname is not None:
            params.append('file={}'.format(fname))
        if dur is not None:
            params.append('duration={:d}'.format(dur))
        if units is not None:
            params.append('durationunits={}'.format(units))
        cmd = 'Recording {:}'.format(','.join(params))
        self.send_cmd(cmd)

    def stop_rec(self):
        '''Send a command to the NDIWave server to stop recording.'''
        self.send_cmd('Recording Stop')
