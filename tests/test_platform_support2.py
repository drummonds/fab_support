import unittest

from fabric.api import env

import fab_support
from fab_support.platform_support import env_to_function


class TestEnvToFunction(unittest.TestCase):
    """Testing very simple test files, just to make sure all is well"""

    def test_null(self):
        """Aim is to test env_to_platform, no platform is defined"""
        with self.assertRaises(KeyError):
            env_to_function("demo", "kill_app")

    def test_has_platform(self):
        """Aim is to test env_to_platform, platform is defined"""
        try:
            print(f"version = {fab_support._version.__version__}")
            env["stages"] = {"demo": {"FS_PLATFORM": "heroku"}}
            self.assertEqual(
                fab_support.heroku.kill_app, env_to_function("demo", "kill_app")
            )
            with self.assertRaises(KeyError):
                env_to_function("prod", "kill_app")
        finally:
            del env["stages"]
