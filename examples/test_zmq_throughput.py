from time import sleep

from experimentor import Q_
from experimentor.config import settings
from experimentor.core.publisher import Publisher, Listener
from experimentor.core.subscriber import Subscriber
from experimentor.models.cameras.basler import BaslerCamera

cam = BaslerCamera('da')
cam.initialize()
cam.clear_ROI()
cam.set_acquisition_mode(cam.MODE_CONTINUOUS)
cam.set_ROI((1, 100), (1, 100))
cam.set_exposure(Q_('10ms'))


publisher = Publisher(settings.GENERAL_STOP_EVENT)
publisher.start()

listener = Listener()


def func(frame): print(len(frame))


subscriber = Subscriber(func, 'frame')
subscriber.start()

sleep(2)

cam.trigger_camera()
i = 0
for _ in range(100):
    frames = cam.read_camera()
    i += len(frames)
    listener.publish(frames, 'frame')
    sleep(.01)

print(f'Acquired {i} frames')

subscriber.stop()
publisher.stop()
listener.finish()