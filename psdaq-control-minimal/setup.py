import os
from setuptools import setup, find_packages

VERSION = '3.3.14'

setup(
       name = 'psdaq-control-minimal',
       license = 'LCLS II',
       description = 'LCLS II DAQ control bits needed for hutch python',
       version = VERSION,
       packages = 'psdaq.control'
)
