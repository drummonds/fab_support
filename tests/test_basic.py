import unittest

from fabric.api import local, lcd

from tests.utils import verbose


class TestBasicFabSupport(unittest.TestCase):

    def test_list(self):
        """Aim is to run fab --list making sure we are running fab in the correct test directory"""
        with lcd('basic'):
            # Check staging and fabfile are correct
            result = local('fab --list', capture=True)
            if verbose():
                print(result)
            self.assertNotRegex(result, 'builds source and wheel', 'Should not be using main fabfile')
            self.assertRegex(result, 'test_demo_fab_file', 'should be using local fab file with local task')
            self.assertRegex(result, 'list_stages', 'Should have task list_stages')

    def test_list_stages(self):
        """Should have one and only demo when you list stages"""
        with lcd('basic'):
            # Check staging and fabfile are correct
            result = local('fab fab_support.list_stages', capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, 'demo', 'demo stage')

    def test_list_stages2(self):
        """Should have one and only demo when you list stages"""
        with lcd('basic2'):
            # Check staging and fabfile are correct
            result = local('fab fab_support.list_stages', capture=True)
            if verbose():
                print(result)
            self.assertRegex(result, 'demo', 'demo stage')
            self.assertRegex(result, 'tag:456', 'production stage')
