from time import sleep

import zmq


ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect('192.168.0.100:1234')
sub.setsockopt(zmq.SUBSCRIBE, b"")

i = 0
while True:
    event = sub.poll(0)
    if not event:
        sleep(.005)
        continue
    i += 1
    data = sub.recv_pyobj()
    print(f'Got {i} frames', end='\r')
