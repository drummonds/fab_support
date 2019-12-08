import json
from random import randrange
import sys

from fabric.api import task, env

# Need to modify path so fab_support is found
# This is only needed to run test fabfile's in a test directory
from pathlib import Path  # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))

# noinspection PyUnresolvedReferences
import fab_support
# noinspection PyUnresolvedReferences
from fab_support import fab_support_function, list_stages

# Going to make or create a filename with a random suffix
# Read from a file if exists
settings_file = Path('fab_support.json')
if settings_file.exists():
    with open(settings_file, 'r') as f:
        settings = json.load(f)
        APP_NAME_PREFIX = settings['APP_NAME_PREFIX']
else:  # Create test file
    # TODO add a test to see if app file exists and then to create another if it doesn't
    APP_NAME_PREFIX = f'fab-support-test-{randrange(0,9990):04d}'
    settings = {'APP_NAME_PREFIX': APP_NAME_PREFIX}
    with open(settings_file, 'w') as f:
        json.dump(settings, f)


# Definition of different environments to deploy to
# using a randomly generated to allow multiple tests of the same module to run together
env['stages'] = {
    'demo': {
        'comment': 'Demo version of Django to be deployed on Heroku',
        'FS_PLATFORM': 'heroku',
        'HEROKU_APP_NAME': f'{APP_NAME_PREFIX}-demo',
        'GIT_BRANCH': 'master',  # Local git branch to copy to Heroku
        'ENV' : {
            'DJANGO_SETTINGS_MODULE': 'demo_django.settings',  # Essential as django doesn't know name of app
        },
    },
}


@task
def identity():
    """Which version of fabfile am I using"""
    try:
        import fab_support
        version = f"fab_support version {fab_support._version.__version__}"
    except ImportError:
        version = 'No fab_support to import'
    print(f"tests/demo_django fabfile {version}")

# Make the following tasks available
# Explicit list so that it is clear what is being imported.

@task
def list_stages():
    """Showing use of a helper function"""
    return fab_support.list_stages()

@task
def kill_app(stage='demo', **kwargs):
    """Kill app"""
    fab_support_function(stage, 'kill_app', **kwargs)


@task
def create_newbuild(stage='demo', **kwargs):
    """Create app with new database"""
    fab_support_function(stage, 'create_newbuild', **kwargs)




