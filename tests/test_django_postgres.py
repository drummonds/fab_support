import os
import unittest

from fabric.api import local, lcd

from tests.utils import verbose


def clean_setup_postgres():
    # Try and remove running apps however relies on demo_django directory not being deleted
    # before try and remove
    if os.path.isdir('tests'):
        my_path = 'tests/demo_django_postgres'
    elif os.path.isdir('template_files'):
        my_path = 'demo_django_postgres'
    else:
        raise Exception
    with lcd(my_path):
        for stage in ('test', 'uat', 'prod'):
            try:
                local(f'fab fab_support.django.kill_app:{stage}')  # Remove any existing run time
            except SystemExit:
                pass


class TestDjangoPostgresSupport(unittest.TestCase):

    def setUp(self):
        clean_setup_postgres()

    def tearDown(self):
        pass

    def test_list(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory"""
        with lcd('demo_django_postgres'):
            # Check staging and fabfile are correct
            result = local('fab --list', capture=True)
            if verbose():
                print(result)
            self.assertNotRegex(result, 'builds source and wheel', 'Should not be using main fabfile')
            self.assertRegex(result, 'test_django_postgres_fab_file', 'should be using local fab file with local task')
            self.assertRegex(result, 'list_stages', 'Should have task list_stages')

    def test_list_stages(self):
        """Should have one and only demo when you list stages"""
        with lcd('demo_django_postgres'):
            # Check staging and fabfile are correct
            result = local('fab fab_support.list_stages', capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, 'Test version of Django', 'demo stage')
            self.assertRegex(result, 'uat', 'UAT stage')
            self.assertRegex(result, 'prod', 'production stage')

    def test_django_postgres(self):
        """
        The Django version is a basic Postgres application.  It has a single app with a single model.
        It is meant to examine the operation of Django app with test, uat and production builds.

        This allows test data and production data to be simulated.

        After running this the directory is kept available.  You can test the server locally as above.

        We will follow the following story:

        Build test with no data
        Build test with test data
        New Build UAT with new production data
        Promote UAT to production
        Build UAT with production data
        Update production
        Promote UAT to production
        Build test with production data


        The Heroku test version that is spun up is a test version at zero cost.
        """
        with lcd('demo_django_postgres'):
            local('fab fab_support.django.create_newbuild:test')  # Build database from scratch
            # local('fab demo fab_support.django.kill_app')  # By default don't let it run after test
