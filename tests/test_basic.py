import unittest

from fabric.api import local, lcd

from tests.utils import verbose


class TestBasicFabSupport(unittest.TestCase):
    """Testing very simple test files, just to make sure all is well"""

    def test_list(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory"""
        with lcd("basic"):
            # Check staging and fabfile are correct
            result = local("fab --list", capture=True)
            lines = result.split("\n")
            num_commands = len(lines) - 2
            if verbose():
                print(result)
            self.assertEqual(2, num_commands, "Should only be two commands")
            self.assertNotRegex(
                result, "builds source and wheel", "Should not be using main fabfile"
            )
            self.assertRegex(
                result,
                "test_demo_fab_file",
                "should be using local fab file with local task",
            )
            self.assertNotRegex(
                result,
                "fab_support.list_stages",
                "Should not have task list_stages as not connected.",
            )
            result2 = local("fab identity", capture=True)
            self.assertRegex(
                result2,
                "tests/basic fabfile",
                "should be using local fab file with local task",
            )

    def test_env_to_platform(self):
        """Aim is to test env_to_platform, no platform is defined"""

    def test_list2(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory"""
        with lcd("basic2"):
            # Check staging and fabfile are correct
            result = local("fab --list", capture=True)
            if verbose():
                print(result)
            lines = result.split("\n")
            num_commands = len(lines) - 2
            self.assertEqual(3, num_commands, "Should only be three commands")
            self.assertNotRegex(
                result, "builds source and wheel", "Should not be using main fabfile"
            )
            self.assertRegex(
                result,
                "test_demo2_fab_file",
                "should be using local fab file with local task",
            )
            self.assertNotRegex(
                result,
                "fab_support.list_stages",
                "Should not have task list_stages as not connected.",
            )
            self.assertRegex(
                result, "list_stages", "Should have task list_stages as now connected."
            )
            result2 = local("fab identity", capture=True)
            self.assertRegex(
                result2,
                "tests/basic2 fabfile",
                "should be using local fab file with local task",
            )

    def test_list_stages2(self):
        """Should have one and only demo when you list stages"""
        with lcd("basic2"):
            # Check staging and fabfile are correct
            result = local("fab list_stages", capture=True)
            if verbose():
                print(result)
            lines = result.split("\n")
            print(f"lines = {lines}")
            num_stages = (
                len(lines) - 3
            )  # CR and Done are added for implemenation of a task
            self.assertEqual(2, num_stages, "Should only be two stages")
            self.assertRegex(result, "demo", "demo stage")
            self.assertRegex(result, "tag:456", "production stage")
            result2 = local("fab identity", capture=True)
            self.assertRegex(
                result2,
                "tests/basic2 fabfile",
                "should be using local fab file with local task",
            )
