# coding=utf-8

"""
Unoffical Korail(Korea Railroad Corporation) API
~~~~~~~~~~~~~~~~~~~~~

`letskorail` module helps to book trains on Python (3.6+)

Basic usage:

  >>> import letskorail
  >>> korail = letskorail.korail()

Login:

  >>> user = korail.login('id', 'password')
  >>> vars(user)


See more: 

https://github.com/bsangmin/letskorail/sample.py

"""

from .korail import Korail
