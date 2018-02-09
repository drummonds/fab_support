import unittest

from fab_support import set_stages, copy_null, copy_file
from fabric.api import local


class TestBasicFabSupport(unittest.TestCase):

    def test_set_stages(self):
        # Can you call it
        # Definition of different environments to deploy to
        set_stages (globals(), {
            'testhost': {
                'comment': 'stage: Local build and serving from output directory',
                'config_file': 'local_conf.py',
                'destination': '',
                'copy_method': copy_null,
                'SITEURL': 'http://localhost:8000',
                'PORT': 8000,
            },
            'test_file_host': {
                'comment': 'stage: For serving locally on this computer in another directory. ',
                'config_file': 'local_conf.py',
                # Tried desitation as %UserProfile%/Cloud... but it didn't work.
                'destination': './sites/www.test.info',
                'copy_method': copy_file,
                'SITEURL': 'file:///./sites/www.test2.info',
            },
        })


    def test_list(self):
        """Aim is to run fab --list using the current version of fab-support"""
        result = local('cd',capture=True)
        print(result)
        result = local('fab --list',capture=True)
        print(result)
        self.assertNotRegex(result,'builds source and wheel','Should not be using main fabfile')
        self.assertRegex(result,'test_fab_file','Testing local fab')  # should be using local fab file
