import json
import os
from pathlib import Path
import shutil
from time import sleep
import unittest

from fabric.api import local, lcd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from tests.utils import verbose


def clean_setup():
    # Try and remove running apps however relies on demo_django directory not being deleted
    # before try and remove
    if os.path.isdir("tests"):
        my_path = "tests/demo_django"
        my_path2 = "tests/"
    elif os.path.isdir("template_files"):
        my_path = "demo_django"
        my_path2 = ""
    else:
        raise Exception
    with lcd(my_path):
        try:
            # Calling fabric in local test directory
            # This is to kill the OLD app, the new app which will be created will have a new name
            local("fab kill_app:demo")
        except SystemExit:
            pass
    # bodge to get .git file delete keeps giving a PermissionError after testing about a git file
    # The file is probably open with node
    try:
        with lcd(my_path):
            local("del /F /S /Q /A .git", capture=True)  # Get rid of output
    except (FileNotFoundError, SystemExit):
        pass
    with lcd(my_path2):
        try:
            shutil.rmtree(my_path2 + "demo_django")
        except FileNotFoundError:
            result = local("dir", capture=True)
            print("== Failed to remove tree ==")
            print(result)


def clean_test_django():
    clean_setup()
    print("Cleaned test_django extras")


class TestHerokuDeployment(unittest.TestCase):
    """
    This is a set of tests to test a very simple deployment to Heroku.
    A new project is created and with a few template files it is then pushed to Heroku
    """

    def setUp(self):
        """Create a test django project"""

        def copy_local_file(source, destination, suffix=""):
            """Copy a local template file to the demo_django directory """
            local(
                "copy "
                + str(Path("template_files") / source)
                + " "
                + str(Path("demo_django") / destination)
                + suffix
            )

        clean_setup()
        local("django-admin startproject demo_django")
        # TODO convert paths to windows and linux
        copy_local_file("demo_django_fabfile.py", "fabfile.py")  # Automation tasks
        copy_local_file("demo_django.env", ".env")  # Secrets managment
        copy_local_file(
            "demo_django_Procfile", "Procfile"
        )  # Workers required for Heroku/dokku
        copy_local_file("demo_Pipfile", "Pipfile")  # Python env
        copy_local_file("demo_Pipfile.lock", "Pipfile.lock")  # Environment lock
        copy_local_file(
            "demo_django_settings.py", "demo_django/settings.py", suffix=" /Y"
        )  # Need to customise
        # for collect statics (alternative would be to ignore collect static)
        # Setup a git for Heroku to use to deploy demo_django
        local("git init demo_django")
        with lcd("demo_django"):
            local(
                "mkdir static"
            )  # Heroku needs a place to put static files in collectstatic and won't create it.
            local(
                "copy ..\\template_files\\demo_django_fabfile.py static\\fabfile.py"
            )  # To make git recognise it
            local("git add .")
            local("git commit -m 'start'")

    def tearDown(self):
        """If you want to look at the test environment then uncomment this."""
        try:
            local("fab kill_app:demo")  # Remove any existing run time
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
                local("fab kill_app:demo")  # Remove any existing run time
            except SystemExit:
                pass
            local("fab create_newbuild:demo")  # Build application from scratch
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
