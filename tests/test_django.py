import os
import pathlib
import shutil
import unittest

from fabric.api import local, lcd

from fab_support import set_stages, copy_null
from tests.test_utils import remove_tree


def clean_test_set_stages():
    remove_tree(('demo_testhost486',))


def clean_setup():
    # Try and remove running apps however relies on demo_django directory not being deleted
    # before try and remove
    if os.path.isdir('tests'):
        my_path = 'tests/demo_django'
        my_path2 = 'tests/'
    elif os.path.isdir('template_files'):
        my_path = 'demo_django'
        my_path2 = ''
    else:
        raise Exception
    with lcd(my_path):
        try:
            local('fab demo fab_support.django.kill_app')  # Remove any existing run time
        except SystemExit:
            pass
    # bodge to get .git file delete keeps giving a PermissionError after testing about a git file
    try:
        with lcd(my_path):
            local('del /F /S /Q /A .git')
            pass
    except (FileNotFoundError, SystemExit):
        pass
    with lcd(my_path2):
        try:
            shutil.rmtree(my_path2+'demo_django')
        except FileNotFoundError:
            result = local('dir', capture=True)
            print('== Failed to remove tree ==')
            print(result)


def clean_test_django():
    clean_test_set_stages()
    clean_setup()
    print('Cleaned test_django extras')


class TestBasicFabSupport(unittest.TestCase):

    def setUp(self):
        clean_setup()
        local('django-admin startproject demo_django')
        # TODO convert paths to windows and linux
        local('copy template_files\\demo_django_fabfile.py demo_django\\fabfile.py')
        local('copy template_files\\demo_django.env demo_django\\.env')  # Need to have an environment for secrets
        local('copy template_files\\demo_django_Procfile demo_django\\Procfile')  # Need to a Procfile to tell
        # heroku what types of workers you need
        local('copy template_files\\demo_requirements.txt demo_django\\requirements.txt')  # Need to tell Heroku that
        # this is a python project and what is needed in production
        local(
            'copy template_files\\demo_django_settings.py demo_django\\demo_django\\settings.py /Y')  # Need to customise
        # for collect statics (alternative would be to ignore collect static)
        # Setup a git for Heroku to use to deploy demo_django
        local('git init demo_django')
        with lcd('demo_django'):
            local('mkdir static')  # Heroku needs a place to put static files in collectstatic and won't create it.
            local('copy ..\\template_files\\demo_django_fabfile.py static\\fabfile.py')  # To make git recognise it
            local('git add .')
            local("git commit -m 'start'")

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
        clean_test_set_stages()
        # Now actually create a test environment and see if actually working
        pathlib.Path("demo_testhost486").mkdir(exist_ok=True)
        local(
            'copy template_files\\demo_testhost486_fabfile.py demo_testhost486\\fabfile.py')  # TODO convert to windows and linux
        with lcd('demo_testhost486'):
            result = local('fab --list', capture=True)
        print(result)
        self.assertRegex(result, 'test486', 'Using test486 fabfile should have set up demo using set_stages')
        self.assertRegex(result, 'test486_fab_file', 'The fabfile has defined a new task.')

    def test_got_heroku_and_build(self):
        """
        The Django version is meant to be as simple as possible. eg it is running from a sqlite database even
        though it has a Postgres Database available.
        After running this the directory is kept available.  You can test the server locally by:
        - running the dev environment
        - switching to tests\demo_django
        - run `python manage.py runserver`
        - open localhost:8000

        The Heroku test version that is spun up is a test version at zero cost.
        This should be made into another functional test.
        """
        with lcd('demo_django'):
            # Check staging and fabfile are correct
            result = local('fab --list', capture=True)
            self.assertRegex(result, 'demo', 'demo stage')
            self.assertRegex(result, 'test_demo_django_fab_file', 'The fabfile has defined a new task.')
            try:
                local('fab demo fab_support.django.kill_app')  # Remove any existing run time
            except SystemExit:
                pass
            local('fab demo fab_support.django.create_newbuild')  # Build database from scratch

    def test_got_local_fabfile(self):
        with lcd('demo_django'):
            result = local('fab --list', capture=True)
        print(result)
        self.assertNotRegex(result, 'test_fab_file', 'Should not be using test fabfile')
        self.assertRegex(result, 'test_demo_django_fab_file',
                         'Testing local django fab')  # should be using local fab file

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
    # local('fab demo fab_support.django.kill_app')  # By default don't let it run after test
