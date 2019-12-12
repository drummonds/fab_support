import json
import os
from pathlib import Path
import shutil
from time import sleep
import unittest

from fabric.api import local, lcd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from tests.django_demo_utils import clean_setup, django_demo_setup
from tests.utils import verbose


class TestHerokuDeployment(unittest.TestCase):
    """
    This is a set of tests to test a very simple deployment to Heroku.
    A new project is created and with a few template files it is then pushed to Heroku

    The routines in fab_support are called indirectly via fabric.
    """

    def setUp(self):
        """Create a test django project"""
        django_demo_setup(
            platform="heroku"
        )  # Only need to specify platform so as to kill previous instances

    def tearDown(self):
        """If you want to look at the test environment then uncomment this."""
        try:
            clean_setup(platform="heroku")
            local("fab kill_app:demo_heroku")  # Remove any existing run time
            pass
        except SystemExit:
            pass

    def test_list_heroku(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory.
        Also checks on list_stages

        This also excercises the setup and tear down."""
        with lcd("demo_django"):
            # Check staging and fabfile are correct
            result = local("fab --list", capture=True)
            if verbose():
                print(result)
            self.assertNotRegex(
                result, "builds source and wheel", "Should not be using main fabfile"
            )
            self.assertNotRegex(
                result, "fab_support.django.build_app", "Should not be a task"
            )
            self.assertNotRegex(
                result, "fab_support.list_stages", "Should not be a task"
            )
            self.assertNotRegex(
                result, "fab_support.django.list_stages", "Should have task list_stages"
            )
            self.assertRegex(result, "list_stages", "Should have task list_stages")
            result2 = local("fab identity", capture=True)
            self.assertRegex(
                result2,
                "tests/demo_django fabfile",
                "should be using local fab file with local task",
            )

    def test_list_stages(self):
        """Should have one and only demo when you list stages"""
        with lcd("demo_django"):
            # Check staging and fabfile are correct
            result = local("fab list_stages", capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, "Demo version of Django", "demo stage")

    def test_list_apps(self):
        """Should run but don't know what will be in the list"""
        with lcd("demo_django"):
            # Check staging and fabfile are correct
            result = local("fab list_app_names:demo_heroku", capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, "Done", "Can't call list_app_names without error")

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
        with lcd("demo_django"):
            # Check staging and fabfile are correct
            try:
                local("fab kill_app:demo_heroku")  # Remove any existing run time
            except SystemExit:
                pass
            local("fab create_newbuild:demo_heroku")  # Build application from scratch
            # Get Url
            settings_file = Path("demo_django/fab_support.json")
            with open(settings_file, "r") as f:
                settings = json.load(f)
                heroku_url = (
                    f"https://{settings['APP_NAME_PREFIX']}-demo.herokuapp.com/"
                )
            # What is the URL
            try:
                options = Options()
                options.add_argument("-headless")  # Run headless for CI testing
                # If you want to see then switch this off
                self.browser = webdriver.Firefox(options=options)
                self.browser.get(heroku_url)
                self.assertIn(
                    "django",
                    self.browser.find_element_by_tag_name("h2").text,
                    "Should be looking at the Django home page",
                )
            finally:
                try:
                    pass
                    # self.browser.close()
                except AttributeError:  # Problem created browser
                    pass
