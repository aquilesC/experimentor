from time import perf_counter

import zmq

from experimentor.models.devices.cameras.basler.basler import BaslerCamera


cam = BaslerCamera('p')
cam.initialize()

context = zmq.Context()
pusher = context.socket(zmq.PUSH)
pusher.bind(f"tcp://*:1234")

t0 = perf_counter()
i = 0
while True:
    try:
        cam.trigger_camera()
        ans = cam.read_camera()[0]
        pusher.send(ans, 0, copy=True, track=False)
        i += 1
        print(f'Sent {i} frames, {i/(perf_counter()-t0)} fps', end='\r')
    except KeyboardInterrupt:
        break

pusher.close()
cam.finalize()
