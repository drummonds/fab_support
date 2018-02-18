import unittest

from fab_support.django import install_heroku_plugins

class TestHeroku(unittest.TestCase):

    def test_heroku(self):
        self.assertTrue(install_heroku_plugins([]), "install_heroku_plugins failed")
        self.assertTrue(install_heroku_plugins(['heroku-cli-oauth']), "install_heroku_plugins failed")
