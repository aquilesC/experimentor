from time import time

from experimentor import Q_
from experimentor.models.devices.cameras.basler.basler import BaslerCamera


cam = BaslerCamera('p')
cam.initialize()

cam.exposure = Q_('10ms')

t0 = time()
i = 0
while True:
    try:
        cam.trigger_camera()
        ans = cam.read_camera()[0]
        print(f'Acquired {i} frames, {i/(time()-t0)} fps', end='\r')
    except KeyboardInterrupt:
        break

cam.finalize()
