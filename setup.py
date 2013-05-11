try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(name='cycles',
      version='0.1',
      description='Menstrual cycle application',
      install_requires={'python-dateutil>=2.1',},
      entry_points={
            'console_scripts': [
                'cycles = cycles',
            ],
        },
      author='jmjordan',
      url='http://github.com/jmjordan/cycles',
      py_modules=['cycles'],
     )