import zmq

ctx = zmq.Context()
pull = ctx.socket(zmq.PULL)
pull.bind('tcp://192.168.0.100:1234')


i = 0
while True:
    i += 1
    data = pull.recv(flags=0, copy=True, track=False)
    print(f'Got {i} frames', end='\r')
