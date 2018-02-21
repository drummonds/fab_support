from fabric.api import task, env

# Need to modify path so fab_support is found
# This is only needed to run test fabfiles in a test directory
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
    'test': {
        'comment': 'Test version of Django to be deployed on Heroku',
        'DJANGO_SETTINGS_MODULE': 'demo_django.settings',  # Essential as django doesn't know name of app
        'HEROKU_APP_NAME': 'fab-support-test-postgres-test',
        'GIT_PUSH': 'git subtree push --prefix tests/demo_django_postgres heroku master',
        'GIT_PUSH_DIR': '../..',
        'GIT_BRANCH': 'master'
    },
    'uat': {
        'comment': 'UAT version of Django to be deployed on Heroku',
        'DJANGO_SETTINGS_MODULE': 'demo_django.settings',  # Essential as django doesn't know name of app
        'HEROKU_APP_NAME': 'fab-support-test-postgres-uat',
        'GIT_PUSH': 'git subtree push --prefix tests/demo_django_postgres heroku master',
        'GIT_PUSH_DIR': '../..',
        'GIT_BRANCH': 'master'
    },
    'prod': {
        'comment': 'Production version of Django to be deployed on Heroku',
        'DJANGO_SETTINGS_MODULE': 'demo_django.settings',  # Essential as django doesn't know name of app
        'HEROKU_APP_NAME': 'fab-support-test-postgres-prod',
        'GIT_PUSH': 'git subtree push --prefix tests/demo_django_postgres heroku master',
        'GIT_PUSH_DIR': '../..',
        'GIT_BRANCH': 'master'
    },
}


@task
def test_django_postgres_fab_file():
    """A test task to show correct file has been loaded"""
    pass
