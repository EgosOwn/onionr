from setuptools import setup, find_packages
import sys, os

version = '0.0.0'

setup(name='onionr',
      version=version,
      description="Decentralized P2P platform",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Kevin Froman',
      author_email='beardog@firemail.cc',
      url='https://github.com/beardog108/onionr',
      license='GPL 3.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'simple_crypt',
          'requests',
          'setuptools',
          'Flask',
          'pycrypto',
          'gnupg'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
