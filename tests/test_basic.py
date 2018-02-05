import unittest

from fab_support import set_stages, copy_null, copy_file


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

