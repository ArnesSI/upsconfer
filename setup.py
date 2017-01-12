from setuptools import setup

import sys
sys.path.insert(0, './upsconfer')
from upsconfer.version import __version__ as VERSION

setup(
    name='upsconfer',
    version=VERSION,
    url='https://github.com/ArnesSI/upsconfer',
    license='GPLv3',
    author='Matej Vadnjal',
    author_email='matej@arnes.si',
    description='upsconfer is a python library to get info and configure UPS devices.',
    packages=['upsconfer'],
    install_requires=['requests', 'lxml']
)
