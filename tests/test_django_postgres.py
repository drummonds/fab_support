import os
import sys
from time import sleep
import unittest

from fabric.api import local, lcd, env
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options

from tests.utils import verbose

from tests.demo_django_postgres import (
    fabfile,
)  # This is to load the env in the call fabfile

#  This can get confusing as there are two levels of fab file being used.


def clean_setup_postgres():
    # Try and remove running apps however relies on demo_django directory not being deleted
    # before try and remove
    if os.path.isdir("tests"):
        my_path = "tests/demo_django_postgres"
    elif os.path.isdir("template_files"):
        my_path = "demo_django_postgres"
    else:
        raise Exception
    with lcd(my_path):
        for stage in ("test", "uat", "prod", "old_prod"):
            try:
                local(f"fab kill_app:{stage}")  # Remove any existing run time
            except SystemExit:
                pass


class TestDjangoPostgresSupport(unittest.TestCase):
    """These tests are done not building an application from start but by using a test application embedded here.
    Like the demo_django we are executing fabric as a nested environment which will be separate from this one."""

    def setUp(self):
        clean_setup_postgres()
        self.stage = "test"  # default

    def tearDown(self):
        """If you want to look at the test environment then uncomment this."""
        try:
            with lcd("demo_django_postgres"):
                # local(f"fab kill_app:{self.stage}")  # Remove any existing run time
                pass
        except SystemExit:
            pass

    def test_list(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory"""
        with lcd("demo_django_postgres"):
            # Check staging and fabfile are correct
            result = local("fab --list", capture=True)
            if verbose():
                print(result)
            self.assertNotRegex(
                result, "builds source and wheel", "Should not be using main fabfile"
            )
            self.assertRegex(
                result,
                "test_django_postgres_fab_file",
                "should be using local fab file with local task",
            )
            self.assertRegex(result, "list_stages", "Should have task list_stages")

    def test_list_stages(self):
        """Should have one and only demo when you list stages"""
        with lcd("demo_django_postgres"):
            # Check staging and fabfile are correct
            result = local("fab list_stages", capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, "Test version of Django", "demo stage")
            self.assertRegex(result, "uat", "UAT stage")
            self.assertRegex(result, "prod", "production stage")

    def test_project_running(self, at_url):
        result = False
        try:
            options = Options()
            options.add_argument("-headless")  # Run headless for CI testing
            # If you want to see then switch this off
            self.browser = webdriver.Firefox(options=options)
            self.browser.get(at_url)
            try:
                found_text = self.browser.find_element_by_tag_name("h1").text
                result = "Fab Support" in found_text
            except NoSuchElementException:  # No h2 tag, so it isn't running
                result = False
        finally:
            try:
                self.browser.close()
            except AttributeError:  # Problem created browser
                pass
        return result

    def demo_project_actually_running(
        self, at_url, expect_running=True, repeats=8, interval=20
    ):
        for i in range(repeats):
            is_running = self.test_project_running(at_url)
            if expect_running == is_running:
                return
            print(f"({i})Waiting for {at_url} project to run")
            sleep(interval)
        # Now we have exhausted the retries and really need to bring this to a quick stop
        sys.exit(
            f"Waited for project at URL '{at_url}' to be up {repeats} times and still failed"
        )

    def test_django_postgres(self):
        """
        The Django version is a basic Postgres application.  It has a single app with a single model.
        It is meant to examine the operation of Django app with test, uat and production builds.

        This allows test data and production data to be simulated.

        The Heroku test version that is spun up is a test version at zero cost to us.
        """
        with lcd("demo_django_postgres"):
            local("fab create_newbuild:test")
        self.demo_project_actually_running(
            "https://fab-support-test-postgres-test.herokuapp.com/"
        )

    def test_typical_progression(self):
        """
        Build UAT
        Promote to Production
        build a second UAT
        Copy the database from Production
        Promote UAT to production
        remove old production  #  once you are comfortable with new production
        """
        with lcd("demo_django_postgres"):
            local("fab create_newbuild:uat")  # Build database from scratch
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-uat.herokuapp.com/"
            )
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-prod.herokuapp.com/",
                expect_running=False,
            )
            local("fab promote_to_prod:uat")  # Build database from scratch
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-uat.herokuapp.com/",
                expect_running=False,
            )
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-prod.herokuapp.com/"
            )
            self.demo_project_actually_running(
                "https://fab-support-test-p-old-prod.herokuapp.com/",
                expect_running=False,
            )
            local("fab create_newbuild:uat")  # Build database from scratch
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-uat.herokuapp.com/"
            )
            local("fab promote_to_prod:uat")  # Build database from scratch
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-uat.herokuapp.com/",
                expect_running=False,
            )
            self.demo_project_actually_running(
                "https://fab-support-test-postgres-prod.herokuapp.com/"
            )
            self.demo_project_actually_running(
                "https://fab-support-test-p-old-prod.herokuapp.com/"
            )
            for stage in ["uat", "prod", "old_prod"]:
                self.stage = stage
                self.tearDown()
