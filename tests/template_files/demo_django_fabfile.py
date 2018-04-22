from fabric.api import task, env

# Need to modify path so fab_support is found
# This is only needed to run test fabfile's in a test directory
import sys
from pathlib import Path  # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))

# noinspection PyUnresolvedReferences
import fab_support
# noinspection PyUnresolvedReferences
import fab_support.django as django

# Definition of different environments to deploy to
env['stages'] = {
    'demo': {
        'comment': 'Demo version of Django to be deployed on Heroku',
        'HEROKU_APP_NAME': 'fab-support-test-demo',
        'GIT_BRANCH': 'master',  # Local git branch to copy to Heroku
        'ENV' : {
            'DJANGO_SETTINGS_MODULE': 'demo_django.settings',  # Essential as django doesn't know name of app
        },
    },
}


@task
def test_demo_django_fab_file():
    """A test task to show correct file has been loaded"""
    pass
