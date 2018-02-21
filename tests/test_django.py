import os
import shutil
import unittest

from fabric.api import local, lcd

from tests.utils import verbose


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
            local('fab fab_support.django.kill_app:demo')  # Remove any existing run time
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

    def test_list(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory"""
        with lcd('demo_django'):
            # Check staging and fabfile are correct
            result = local('fab --list', capture=True)
            if verbose():
                print(result)
            self.assertNotRegex(result, 'builds source and wheel', 'Should not be using main fabfile')
            self.assertRegex(result, 'test_demo_django_fab_file', 'should be using local fab file with local task')
            self.assertRegex(result, 'list_stages', 'Should have task list_stages')

    def test_list_stages(self):
        """Should have one and only demo when you list stages"""
        with lcd('demo_django'):
            # Check staging and fabfile are correct
            result = local('fab fab_support.list_stages', capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, 'Demo version of Django', 'demo stage')

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
                local('fab fab_support.django.kill_app:demo')  # Remove any existing run time
            except SystemExit:
                pass
            local('fab fab_support.django.create_newbuild:demo')  # Build database from scratch
            # TODO add selenium to check that website is up

