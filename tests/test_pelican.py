import os
import shutil
import unittest
from fabric.api import local, env, lcd

from fab_support import copy_null


def clean_test_pelican():
    # Try and remove running apps however relies on demo_django directory not being deleted
    # before try and remove
    if os.path.isdir('tests'):
        my_path = 'tests/'
    elif os.path.isdir('template_files'):
        my_path = ''
    else:
        raise Exception
    with lcd(my_path):
        try:
            shutil.rmtree(my_path + 'demo_django')
        except FileNotFoundError:
            result = local('dir', capture=True)
            print('== Failed to remove tree ==')
            print(result)


class TestBasicFabSupport(unittest.TestCase):

    def test_set_stages(self):
        # Definition of different environments to deploy to
        env['stages'] = {
            'testhost': {
                'comment': 'stage: Local build and serving from output directory',
                'config_file': 'local_conf.py',
                'destination': '',
                'copy_method': copy_null,
                'SITEURL': 'http://localhost:8000',
                'PORT': 8000,
            },
        }
        local('pelican ')
