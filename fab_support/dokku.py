import os

from dotenv import load_dotenv, find_dotenv
from fabric.api import env, run, sudo
from fabric.tasks import execute

from .utils import FabricSupportException


# .env
# Get any required secret environment variables
load_dotenv(find_dotenv())

env.use_ssh_config = True
env.host_string = os.getenv('DOKKU_TEST_SERVER_IP')
env.user = os.getenv('DOKKU_USER')
env.password = os.getenv('DOKKU_PASSWORD')
env.key_filename = "~/.ssh/id_rsa"
env.port = 22


def get_global_environment_variables(stage):
    # Get a number of predefined environment variables from the staging system variables
    # and turn them into globals for use in this script
    # TODO perhaps convert to another method of access
    for global_env in (
        "APP_NAME",
        "PROD_APP_NAME",
        "OLD_PROD_APP_NAME",
        "PRODUCTION_URL",
        "USES_CELERY",
        "GIT_BRANCH",
        "GIT_PUSH",
        "GIT_PUSH_DIR",
        "DJANGO_SETTINGS_MODULE",
    ):
        try:
            globals()[global_env] = env["stages"][stage][global_env]
        except KeyError:
            # This global variable will use the default
            pass

def is_production():
    return APP_NAME[-4:].lower() == "prod"


def _list_app_names():
    """Return a list of app names"""
    capture = sudo('dokku apps:list')
    result=[]
    for line in capture.split('\n'):
        line = line.replace('\r','')
        if line not in {'','=====> My Apps'}:
            result.append(line)
    return result

def list_app_names(stage):
    """list app names as a fabric task
    :param: stage is not required for _list_app_names but is a parameter to make compatible with general calling
    method
    :return: List of apps names"""
    return _list_app_names()

def _kill_app(stage):
    """see kill app"""
    print(f'deleting {APP_NAME} on dokku')
    sudo(f'echo "{APP_NAME}" | ssh "{APP_NAME}" apps:destroy')


def kill_app(stage, safety_on=True):
    """Kill app notice that to the syntax for the production version is:
    fab the_stage kill_app:False"""
    get_global_environment_variables(stage)
    print(f'asking to delete {APP_NAME} on dokku')
    if APP_NAME in _list_app_names():
        if not (is_production() and not safety_on):
            _kill_app()

# #############
def _create_newbuild(stage):
    """This builds the database and waits for it be ready.  It is is safe to run and won't
    destroy any existing infrastructure.
    It is expecting to run within the top level of the project that is going to be pushed to external dokku machine
    The dokku target is set up in .env"""
    sudo(
        f"dokku apps:create {APP_NAME}"
    )
    # # This is where we create the database.  The type of database can range from hobby-dev for small
    # # free access to standard for production quality docs
    # local(
    #     f"heroku addons:create heroku-postgresql:{HEROKU_POSTGRES_TYPE} --app {HEROKU_APP_NAME}"
    # )
    # local(f"heroku addons:create cloudamqp:lemur --app {HEROKU_APP_NAME}")
    # local(f"heroku addons:create papertrail:choklad --app {HEROKU_APP_NAME}")
    # # set database backup schedule
    # repeat_run_local(
    #     f"heroku pg:wait --app {HEROKU_APP_NAME}"
    # )  # It takes some time for DB so wait for it
    # # When wait returns the database is not necessarily completely finished preparing itself.  So the next
    # # command could fail (and did on testing on v0.1.6)
    # repeat_run_local(f"heroku pg:backups:schedule --at 04:00 --app {HEROKU_APP_NAME}")
    # # Already promoted as new local('heroku pg:promote DATABASE_URL --app my-app-prod')
    # # Leaving out and aws and reddis
    # raw_update_app(stage)
    # wait_for_dyno_to_run(HEROKU_APP_NAME)
    # local("heroku run python manage.py check --deploy")  # make sure all ok
    #
    # # Create superuser - the interactive command does not allow you to script the password
    # # So this is a hack  workaround.
    # # Django 1 only
    # # cmd = ('heroku run "echo \'from django.contrib.auth import get_user_model; User = get_user_model(); '
    # #       + f'User.objects.filter(email="""{SUPERUSER_EMAIL}""", is_superuser=True).delete(); '
    # #       + f'User.objects.create_superuser("""{SUPERUSER_NAME}""", """{SUPERUSER_EMAIL}""", """{SUPERUSER_PASSWORD}""")\' '
    # #       + f' | python manage.py shell"')
    # # local(cmd)


def create_newbuild(stage):
    get_global_environment_variables(stage)
    _create_newbuild(stage)

