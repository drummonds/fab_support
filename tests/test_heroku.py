import unittest

from fab_support.heroku import _list_app_names


class TestHerokuInternals(unittest.TestCase):
    """
    This is testing directly in heroku not via fabric
    """

    def test_list_apps(self):
        """Should return a list with an unknown number of items"""
        result = _list_app_names()
        self.assertIsInstance(result,list,'Should return a list')
        print(result)
