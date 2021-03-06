from time import perf_counter, time

import zmq

ctx = zmq.Context()
pull = ctx.socket(zmq.PULL)
pull.connect('tcp://192.168.0.100:1234')


i = 0
t0 = time()
while True:
    i += 1
    data = pull.recv(flags=0, copy=True, track=False)
    print(f'Got {i} frames, {i/(time()-t0)} fps', end='\r')
