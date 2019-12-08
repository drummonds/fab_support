# Need to modify path so fab_support is found
# This is only needed to run test fabfiles in a test directory
from pathlib import Path  # if you haven't already done so
import sys

from fabric.api import task, env

from fab_support import fab_support_function, list_stages


file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))

# noinspection PyUnresolvedReferences
import fab_support

# noinspection PyUnresolvedReferences
import fab_support.heroku as django

# Definition of different environments to deploy to
env["stages"] = {
    "test": {
        "comment": "Test version of Django to be deployed on Heroku",
        "FS_PLATFORM": "heroku",
        "HEROKU_APP_NAME": "fab-support-test-postgres-test",
        "HEROKU_PROD_APP_NAME": "fab-support-test-postgres-prod",  # Can be a source of data
        "GIT_PUSH": "git subtree push --prefix tests/demo_django_postgres heroku master",
        "GIT_PUSH_DIR": "../..",
        "GIT_BRANCH": "master",
        "ENV": {
            "DJANGO_SETTINGS_MODULE": "demo_django.settings"  # Essential as django doesn't know name of app
        },
    },
    "uat": {
        "comment": "UAT version of Django to be deployed on Heroku",
        "FS_PLATFORM": "heroku",
        "HEROKU_APP_NAME": "fab-support-test-postgres-uat",
        "HEROKU_PROD_APP_NAME": "fab-support-test-postgres-prod",
        "HEROKU_OLD_PROD_APP_NAME": "fab-support-test-p-old-prod",
        "HEROKU_POSTGRES_TYPE": "hobby-dev",  # Replicate production but expensive
        "GIT_PUSH": "git subtree push --prefix tests/demo_django_postgres heroku master",
        "GIT_PUSH_DIR": "../..",
        "GIT_BRANCH": "master",
        "ENV": {
            "DJANGO_SETTINGS_MODULE": "demo_django.settings"  # Essential as django doesn't know name of app
        },
    },
    "prod": {
        "comment": "Production version of Django to be deployed on Heroku",
        "FS_PLATFORM": "heroku",
        "HEROKU_APP_NAME": "fab-support-test-postgres-prod",
        "HEROKU_PROD_APP_NAME": "fab-support-test-postgres-prod",
        "HEROKU_OLD_PROD_APP_NAME": "fab-support-test-p-old-prod",
        "HEROKU_POSTGRES_TYPE": "hobby-dev",  # Replicate production but expensive
        "GIT_PUSH": "git subtree push --prefix tests/demo_django_postgres heroku master",
        "GIT_PUSH_DIR": "../..",
        "GIT_BRANCH": "master",
        "ENV": {
            "DJANGO_SETTINGS_MODULE": "demo_django.settings"  # Essential as django doesn't know name of app
        },
    },
    "old_prod": {
        "comment": "Created by others on promotion, listed here to make sure will be deleted by clean up",
        "FS_PLATFORM": "heroku",
        "HEROKU_APP_NAME": "fab-support-test-p-old-prod",
    },
}


@task
def test_django_postgres_fab_file():
    """A test task to show correct file has been loaded"""
    pass


@task
def list_stages():
    """Showing use of a helper function"""
    return fab_support.list_stages()


@task
def kill_app(stage="test", **kwargs):
    """Kill app"""
    fab_support_function(stage, "kill_app", **kwargs)


@task
def create_newbuild(stage="test", **kwargs):
    """create_newbuild"""
    fab_support_function(stage, "create_newbuild", **kwargs)


@task
def promote_to_prod(stage="uat", **kwargs):
    """default is to promote uat to prod, and prod to old_prod where the destinations for prod and old_prod are
    defined in the environment variabls for this stage"""
    fab_support_function(stage, "promote_to_prod", **kwargs)
