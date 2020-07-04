import zmq

from experimentor.models.devices.cameras.basler.basler import BaslerCamera


cam = BaslerCamera('p')
cam.initialize()

context = zmq.Context()
pusher = context.socket(zmq.PUSH)
pusher.bind(f"udp://*:1234")

i = 0
while True:
    try:
        cam.trigger_camera()
        ans = cam.read_camera()[0]
        pusher.send(ans, 0, copy=True, track=False)
        i+=1
        print(f'Sent {i} frames', end='\r')
    except KeyboardInterrupt:
        break

pusher.close()
cam.finalize()
