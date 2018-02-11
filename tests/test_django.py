import pathlib
import os
import unittest

from fabric.api import local, lcd

from fab_support import set_stages, copy_null
from fabfile import remove_tree


class TestBasicFabSupport(unittest.TestCase):

    def setUp(self):
        remove_tree(('demo_django',))
        local('django-admin startproject demo_django')
        local('copy template_files\\demo_django_fabfile.py demo_django\\fabfile.py')  # TODO convert to windows and linux
        local('copy template_files\\demo_django.env demo_django\\.env')  # TODO convert to windows and linux
        local('copy template_files\\demo_django_Procfile demo_django\\Procfile')  # TODO convert to windows and linux
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
        # Now actually create a test environment and see if actually working
        remove_tree(('demo_testhost486',))
        pathlib.Path("demo_testhost486").mkdir(exist_ok=True)
        local('copy template_files\\demo_testhost486_fabfile.py demo_testhost486\\fabfile.py')  # TODO convert to windows and linux
        with lcd('demo_testhost486'):
            result = local('fab --list', capture=True)
        print(result)
        self.assertRegex(result, 'test486', 'Using test486 fabfile should have set up demo using set_stages')
        self.assertRegex(result, 'test486_fab_file', 'The fabfile has defined a new task.')

    def test_got_heroku_and_build(self):
        with lcd('demo_django'):
            # Check staging and fabfile are correct
            result = local('fab --list', capture=True)
            self.assertRegex(result, 'demo', 'demo stage')
            self.assertRegex(result, 'test_demo_django_fab_file', 'The fabfile has defined a new task.')
            local('fab demo fab_support.django.kill_app')  # Build database from scratch
            local('fab demo fab_support.django.create_newbuild')  # Build database from scratch

    def test_got_local_fabfile(self):
        with lcd('demo_django'):
            result = local('fab --list', capture=True)
        print(result)
        self.assertNotRegex(result, 'test_fab_file', 'Should not be using test fabfile')
        self.assertRegex(result, 'test_demo_django_fab_file', 'Testing local django fab')  # should be using local fab file

    # This was an experiment but couldn't make wsl run from local
    # def test_got_wsl(self):
    #     """Check that have wsl version of heroku and is logged in."""
    #     result = local('bash ls', capture=True)
    #     self.assertRegex(result, 'Apps\:', 'Make sure have heroku working and logged in')
    #
    # def test_got_wsl_heroku(self):
    #     """Check that have wsl version of heroku and is logged in."""
    #     result = local('bash /usr/bin/heroku status', capture=True)
    #     self.assertRegex(result, 'Apps\:', 'Make sure have heroku working and logged in')
