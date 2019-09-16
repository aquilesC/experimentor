"""
    File to show what is the goal of the package.

    .. sectionauthor:: Aquiles Carattino
"""
from experimentor.models import Model
from examples.measurement.models.camera import Camera
from examples.measurement.experiment.track import Track

tracking = Track.config_from_file()
tracking.config_from_file('config.py')

if __name__ == "__main__":
    # print(issubclass(Camera, Model))
    tracking.run()