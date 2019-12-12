import unittest

from tests.django_demo_utils import clean_setup, django_demo_setup


class TestDemoDjangoUtilities(unittest.TestCase):
    """
    This is some very basic tests of the dokku interface without actually deploying anything.

    Eg can we call various commands and get the results we want.  It uses the basic demo_django setup
    but without actual apps being deployed.  For this see test_django_dokku

    There is not module setup and tear down becuase this is what we are testing.
    """

    def test_file_cleanup(self):
        """Makes sure the clean up works.
        Don't delete the app as this would require the deployment code to work"""
        clean_setup()  # This may or may not do real work
        # And it should be safe to call twice
        clean_setup()  # This should not do anything

    def test_setup_and_teardown(self):
        """"""
        clean_setup()  # Make sure clear to start with
        try:
            django_demo_setup()
        finally:
            clean_setup()  # This should now clear up


