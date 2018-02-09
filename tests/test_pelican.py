import unittest
from fabfile import clean_test
from fabric.api import local


from fab_support import set_stages, copy_null, copy_file


class TestBasicFabSupport(unittest.TestCase):

    def setUp(self):
        # local('pelican-quickstart')
        pass

    def tearDown(self):
        clean_test()

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
        })
        local('pelican ')

