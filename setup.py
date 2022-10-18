from distutils.core import setup

from setuptools import find_packages

with open('experimentor/__init__.py', 'r') as f:
    version_line = f.readline()

version = version_line.split('=')[1].strip().replace("'", "")

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='experimentor',
    version=version,
    packages=find_packages(),
    url='https://github.com/aquilesC/experimentor',
    license='MIT',
    author='Aquiles',
    author_email='aquiles@pythonforthelab.com',
    description='Basic building blocks for controlling complex setups',
    install_requires=[
        'pint==0.18',
        'numpy',
    ],
    python_requires='>=3.8',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
