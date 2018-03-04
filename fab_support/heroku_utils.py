"""
Utilities that work with Heroku
"""
from fabric.api import local
import json
import re
import sys
from time import sleep


def list_databases(app=''):
    """
    List
    :param app: Name of app to use if default '' will return current list
    :return: list of database names
    """
    result = []
    for i in range(5):
        try:
            if app:
                fab_result = json.loads(local(f'heroku info --json --app={app}', capture=True))
            else:
                fab_result = json.loads(local('heroku info --json', capture=True))
            for addon in fab_result['addons']:
                if addon['addon_service']['name'] == 'heroku-postgresql':
                    name = addon['config_vars'][0]
                    if name == 'DATABASE_URL':
                        colour = ''
                    else:
                        # Extract colour from name like 'HEROKU_POSTGRESQL_PURPLE_URL'
                        found = re.search('HEROKU_POSTGRESQL_(.*)_URL', name)
                        colour = found.group(1)
                    result.append([name, colour])
            break
        except IndexError:  # Returned if database config_var are not yet setup
            print(f'Trying to list databases attempt {i} as not yet setup')
            print(f'Returned: {fab_result}')
            sleep(15)
    if result:
        return result
    else:
        sys.exit('Failed to get database list')


def first_colour_database(app=''):
    db_list = list_databases(app)
    for name, colour in db_list:
        if colour:
            return [name, colour]
    return ['', '']  # Not found
