import zmq
from experimentor.models.devices.cameras.basler.basler import BaslerCamera


cam = BaslerCamera('p')
cam.initialize()

ctx = zmq.Context()
publisher = ctx.socket(zmq.PUB)
publisher.bind('tcp://*:1234')


i = 0
while True:
    cam.trigger_camera()
    ans = cam.read_camera()
    publisher.send_pyobj(ans)
    i+=1
    print(f'Sent {i} frames', end='\r')