from distutils.core import setup

setup(
    name='experimentor',
    version='0.2',
    packages=['experimentor', 'experimentor.lib', 'experimentor.models', 'experimentor.models.daq',
              'experimentor.models.laser', 'experimentor.drivers', 'experimentor.drivers.santec',
              'experimentor.drivers.keysight', 'experimentor.experiment'],
    url='https://github.com/uetke/experimentor',
    license='MIT',
    author='Aquiles',
    author_email='aquiles@uetke.com',
    description='Basic building blocks for controlling complex setups',
    install_requires=[
        'pint',
        'numpy',
    ],
    python_requires='>=3.6',
)
