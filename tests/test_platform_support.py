import unittest

from fabric.api import local, lcd, env

from tests.utils import verbose

import fab_support
from fab_support.platform_support import env_to_platform


class TestEnvToPlatform(unittest.TestCase):
    """Testing very simple test files, just to make sure all is well"""

    def test_null(self):
        """Aim is to test env_to_platform, no platform is defined"""
        with self.assertRaises(KeyError):
            env_to_platform("demo")

    def test_empty_env(self):
        """Aim is to test env_to_platform, no platform is defined"""
        try:
            env["stages"] = {"demo": {}}
            with self.assertRaises(KeyError):
                env_to_platform("demo")
        finally:
            del env["stages"]

    def test_has_platform(self):
        """Aim is to test env_to_platform, platform is defined"""
        try:
            env["stages"] = {"demo": {"FS_PLATFORM": "heroku"}}
            self.assertEqual("heroku", env_to_platform("demo"))
            with self.assertRaises(KeyError):
                env_to_platform("prod")
        finally:
            del env["stages"]
