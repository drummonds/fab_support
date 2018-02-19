# -*- coding: utf-8 -*-

"""Top-level package for fab_support."""

__author__ = """Humphrey Drummond"""
__email__ = 'hum3@drummond.info'
__version__ = '0.0.3'


from .django import *
from .env_support import *
# from .pelican import *
from .stages_support import set_stages, list_stages
from .utils import *

