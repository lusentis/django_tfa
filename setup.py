#!/usr/bin/env python

from distutils.core import setup

setup(name='django_tfa',
      version='0.1',
      description='Django Two-Factor Authentication (TFA)',
      author='Simone Lusenti',
      author_email='simone@slusenti.me',
      url='https://github.com/lusentis/django_tfa/',
      packages=['twofactor'],
      package_data={'twofactor': ['templates/*.html']},
)
