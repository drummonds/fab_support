import unittest
from fabric.api import local, lcd
import os

import fab_support
from fab_support import set_stages, copy_null
from fabfile import remove_tree


class TestBasicFabSupport(unittest.TestCase):

    def setUp(self):
        remove_tree(('demo_django',))
        local('django-admin startproject demo_django')
        local('copy template_files\\demo_dango_fabfile.py demo_django\\fabfile.py')  # TODO convert to windows and linux
        local('git init demo_django')

    def tearDown(self):
        pass

    def test_set_stages(self):
        # Can you call it
        # Definition of different environments to deploy to
        set_stages(globals(), {
            'testhost': {
                'comment': 'stage: Local build and serving from output directory',
                'config_file': 'local_conf.py',
                'destination': '',
                'copy_method': copy_null,
                'SITEURL': 'http://localhost:8000',
                'PORT': 8000,
            },
        })

    def test_got_heroku_and_build(self):
        # Can you call it
        # Definition of different environments to deploy to
        result = local('heroku status', capture=True)
        self.assertRegex(result, 'Apps\:')
        os.environ['HEROKU_PREFIX'] = 'fab-support-test-demo'
        local('fab fab_support.django.build_app:master')

    def test_got_local_fabfile(self):
        with lcd('demo_django'):
            result = local('fab --list',capture=True)
        print(result)
        self.assertNotRegex(result,'test_fab_file','Should not be using test fabfile')
        self.assertRegex(result,'test_demo_django_fab_file','Testing local django fab')  # should be using local fab file


