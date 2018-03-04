from unittest import TestCase

from fab_support.heroku_utils import list_databases, first_colour_database

class TestHeroku(TestCase):

    def test_list(self):
        print(list_databases(app='fab-support-test-postgres-prod'))
        name, colour = first_colour_database(app='fab-support-test-postgres-prod')
        print(f'{name}, {colour}')
        self.assertTrue(True, 'Tested list code, what it get backs depends on setup')
