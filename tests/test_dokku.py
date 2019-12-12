import unittest

from fab_support.dokku import _list_app_names


class TestDokkuInternals(unittest.TestCase):
    """
    This is testing directly in dokku not via fabric
    """

    def test_list_apps(self):
        """Should return a list with an unknown number of items"""
        result = _list_app_names()
        self.assertIsInstance(result,list,'Should return a list')
        print(result)
