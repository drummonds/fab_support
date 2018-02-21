import datetime as dt
from fabric.api import env, local, task, lcd
from fabric.operations import require
import json
import os
import re
import time

DJANGO_SETTINGS_MODULE = 'production'  # Which settings configuration to use in Django
HEROKU_APP_NAME = 'fab-support-app-test' # name of this stages Heroku app
HEROKU_PROD_APP_NAME = 'fab-support-app-prod'  # Name of Heroku app which is production, ie source of data
HEROKU_POSTGRES_TYPE = 'hobby-dev'
SUPERUSER_NAME = 'superuser'  # TODO may want to get rid of defaults
SUPERUSER_EMAIL = 'info@demo.com'
# noinspection SpellCheckingInspection
SUPERUSER_PASSWORD = 'akiualsdfha*&(j'  # TODO Need alternative
GIT_PUSH = ''  # Default to false
GIT_PUSH_DIR = '.'  #
GIT_BRANCH = 'master'
USES_CELERY = False


##################################################
# Local utilities
##################################################

def remove_unused_db(stage='uat'):
    """List all databases in use for app, find the main one and remove all the others"""
    data = json.loads(local(f'heroku config --json --app {HEROKU_APP_NAME}', capture=True))
    for k, v in data.items():
        # noinspection SpellCheckingInspection
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v != data['DATABASE_URL']:
                local(f'heroku addons:destroy {k} --app {HEROKU_APP_NAME} --confirm {HEROKU_APP_NAME}')


def default_db_colour(app_name):
    """Return the default database colour of heroku application"""
    data = json.loads(local('heroku config --json --app {0}'.format(app_name), capture=True))
    result = ''
    for k, v in data.items():
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v == data['DATABASE_URL']:
                return k
    # if no colour found then try the long name in database_url
    # raise Exception(f'No color database names found for app {app_name} - create an extra one and it should be ok.')
    return data['DATABASE_URL']


def set_heroku_environment_variables():
    """This sets all the environment variables that a Django recipe needs."""
    local(f"heroku config:set DJANGO_SETTINGS_MODULE={DJANGO_SETTINGS_MODULE} --app {HEROKU_APP_NAME}")
    local(f"heroku config:set PYTHONHASHSEED=random --app {HEROKU_APP_NAME}")
    try:
        allowed_hosts = os.environ['DJANGO_ALLOWED_HOSTS']
    except KeyError:
        allowed_hosts = f'{HEROKU_APP_NAME}.herokuapp.com'
    local(f'heroku config:set DJANGO_ALLOWED_HOSTS="{allowed_hosts}" --app {HEROKU_APP_NAME}')
    # TODO 'DJANGO_SECRET_KEY' needs to be installed or have useful defaults
    not_used = []
    for config in ('DJANGO_SECRET_KEY', 'DJANGO_ADMIN_URL'
                   , 'DJANGO_AWS_ACCESS_KEY_ID', 'DJANGO_AWS_SECRET_ACCESS_KEY', 'DJANGO_AWS_STORAGE_BUCKET_NAME'
                   , 'DJANGO_MAILGUN_API_KEY', 'DJANGO_SERVER_EMAIL', 'MAILGUN_SENDER_DOMAIN'
                   , 'DJANGO_ACCOUNT_ALLOW_REGISTRATION', 'DJANGO_SENTRY_DSN'
                   , 'XERO_CONSUMER_SECRET', 'XERO_CONSUMER_KEY'):
        try:
            local('heroku config:set {}={} --app {}'.format(config, os.environ[config], HEROKU_APP_NAME))
        except KeyError:
            # This environment variable won't be set
            not_used.append(config)
    if not_used:
        print(f'The following config variables were not used: {not_used}')


def raw_update_app():
    """Update of app to latest version"""
    # Put the heroku app in maintenance mode TODO
    set_heroku_environment_variables()  # In case anything has changed
    # connect git to the correct remote repository
    local('heroku git:remote -a {}'.format(HEROKU_APP_NAME))
    # Need to push the branch in git to the master branch in the remote heroku repository
    print(f'GIT_PUSH_DIR = {GIT_PUSH_DIR}, GIT_PUSH = {GIT_PUSH}, GIT_BRANCH = {GIT_BRANCH}')
    if GIT_PUSH == '':  # test for special case probably deploying a subtree
        local(f'git push heroku {GIT_BRANCH}:master')
    else:
        # The command will probably be like this:
        # 'GIT_PUSH': 'git subtree push --prefix tests/my_heroku_project heroku master',
        with lcd(GIT_PUSH_DIR):
            local(GIT_PUSH)
    # Don't need to scale workers down as not using eg heroku ps:scale worker=0
    # Will add guvscale to spin workers up and down from 0
    if USES_CELERY:
        local(f'heroku ps:scale worker=1 -a {HEROKU_APP_NAME}')
    # Have used performance web=standard-1x and worker=standard-2x but adjusted app to used less memory
    # local(f'heroku ps:resize web=standard-1x -a {HEROKU_APP_NAME}')  # Resize web to be compatible with performance workers
    # local(f'heroku ps:resize worker=standard-2x -a {HEROKU_APP_NAME}')  # Resize workers
    # makemigrations should be run locally and the results checked into git
    local('heroku run "yes \'yes\' | python manage.py migrate"')  # Force deletion of stale content types


def install_heroku_plugins(plug_in_list):
    # plugins doesn't support returning --json
    results = local('heroku plugins --core', capture=True)  # returns string or string list
    result_list = results.split('\n')
    plugin_dict = {}
    for result in result_list:
        parts = result.split(' ')
        try:
            plugin_dict[parts[0]] = parts[1]
        except IndexError:
            plugin_dict[parts[0]] = ''
    for plug_in in plug_in_list:
        if not plug_in in plugin_dict:
            local(f'heroku plugins:install {plug_in}')  # installed in local toolbelt not on app
            # If it fails then it really is a failure not just it has already been installed.
    return True  # Got to end and all installed
    # print(f'|{results}|')


# #############
def _create_newbuild():
    """This builds the database and waits for it be ready.  It is is safe to run and won't
    destroy any existing infrastructure."""
    local(f'heroku create {HEROKU_APP_NAME} --buildpack https://github.com/heroku/heroku-buildpack-python --region eu')
    # This is where we create the database.  The type of database can range from hobby-dev for small
    # free access to standard for production quality docs
    local(f'heroku addons:create heroku-postgresql:{HEROKU_POSTGRES_TYPE} --app {HEROKU_APP_NAME}')
    local(f'heroku addons:create cloudamqp:lemur --app {HEROKU_APP_NAME}')
    local(f'heroku addons:create papertrail:choklad --app {HEROKU_APP_NAME}')
    # Add guvscale processing to allow celery queue to be at zero
    install_heroku_plugins(['heroku-cli-oauth', 'heroku-guvscale'])
    # start of configuring guvscale to autoscale
    # local(f'heroku guvscale:getconfig --app {HEROKU_APP_NAME}')
    # set database backup schedule
    local(f'heroku pg:wait --app {HEROKU_APP_NAME}')  # It takes some time for DB so wait for it
    local(f'heroku pg:backups:schedule --at 04:00 --app {HEROKU_APP_NAME}')
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app my-app-prod')
    # Leaving out and aws and reddis
    raw_update_app()
    local('heroku run python manage.py check --deploy')  # make sure all ok

    # Create superuser - the interactive command does not allow you to script the password
    # So this is a hack  workaround.
    # Django 1 only
    # cmd = ('heroku run "echo \'from django.contrib.auth import get_user_model; User = get_user_model(); '
    #       + f'User.objects.filter(email="""{SUPERUSER_EMAIL}""", is_superuser=True).delete(); '
    #       + f'User.objects.create_superuser("""{SUPERUSER_NAME}""", """{SUPERUSER_EMAIL}""", """{SUPERUSER_PASSWORD}""")\' '
    #       + f' | python manage.py shell"')
    # local(cmd)


def get_global_environment_variables(stage):
    # Get a number of predefined environment variables from the staging system variables
    # and turn them into globals for use in this script
    # TODO perhaps convert to another method of access
    for global_env in ('HEROKU_APP_NAME', 'HEROKU_PROD_APP_NAME', 'HEROKU_POSTGRES_TYPE',
                       'SUPERUSER_NAME', 'USES_CELERY',
                       'SUPERUSER_EMAIL', 'SUPERUSER_PASSWORD',
                       'GIT_BRANCH', 'GIT_PUSH', 'GIT_PUSH_DIR',
                       'DJANGO_SETTINGS_MODULE'):
        try:
            globals()[global_env] = env['stages'][stage][global_env]
        except KeyError:
            # This global variable will use the default
            pass


@task
def create_newbuild(stage):
    get_global_environment_variables(stage)
    _create_newbuild()


def is_production():
    return HEROKU_APP_NAME[-4:].lower() == 'prod'


def _kill_app():
    """see kill app"""
    local(f'heroku destroy {HEROKU_APP_NAME} --confirm {HEROKU_APP_NAME}')


@task
def kill_app(stage, safety_on=True):
    """Kill app notice that to the syntax for the production version is:
    fab the_stage kill_app:False"""
    # Todo Add steps to verify that it exists (optional) and make sure it is deleted at the end
    if not (is_production() and not safety_on):
        get_global_environment_variables(stage)
        _kill_app()


@task
def build_uat():
    """Build a new uat environments"""
    build_app()


@task
def build_app(stage='uat'):
    """Build a test environment. Default is uat.
    So fab build_app  is equivalent to fab build_app:uat  and to fab build_app:stage=uat
    so can build a test branch with:
        fab build_app:stage=test"""
    start_time = time.time()
    get_global_environment_variables(stage)
    try:
        _kill_app()
    except SystemExit:
        if stage != 'prod':
            pass  # ignore errors in case original does not exist
        else:
            raise Exception('Must stop if an error when deleting a production database.')
    _create_newbuild()
    local(f'fab transfer_database_from_production:{stage}')
    # makemigrations should be run locally and the results checked into git
    # Need to migrate the old database schema from the master production database
    local('heroku run "yes \'yes\' | python manage.py migrate"')  # Force deletion of stale content types
    # Calculate time
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f'Run time = {runtime} Completed at: {dt.datetime.now()}')


@task
def create_new_db(stage='uat'):
    """Just creates a new database for this instance."""
    HEROKU_APP_NAME = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], stage)
    # Put the heroku app in maintenance move
    m = local('heroku addons:create heroku-postgresql:hobby-basic --app {0}'.format(HEROKU_APP_NAME), capture=True)
    m1 = m.replace('\n',' ')  # Convert to a single string
    print(f'>>>{m1}<<<')
    found = re.search('Created\w*(.*)\w*as\w*(.*)\w* Use', m1)
    db_name = found.group(1)
    colour = found.group(2)
    print(f'DB colour = {colour}, {db_name}')
    local('heroku pg:wait')  # It takes some time for DB so wait for it
    return colour, db_name


def _transfer_database_from_production(stage='test', clean=True):
    """This is usually used for making a copy of the production database for a UAT staging
    or test environment.  It can also be used to upgrade the production environment from one
    database plan to the next. """
    # Put the heroku app in maintenance move
    try:
        local('heroku maintenance:on --app {} '.format(HEROKU_APP_NAME))
        colour, db_name = create_new_db(stage)  # color is ?
        # Don't need to scale workers down as not using eg heroku ps:scale worker=0
        local(f'heroku pg:copy {HEROKU_PROD_APP_NAME}::DATABASE_URL {colour} --app {HEROKU_APP_NAME} --confirm {HEROKU_APP_NAME}')
        local(f'heroku pg:promote {colour}')
        if clean:
            remove_unused_db(stage)
    finally:
        local('heroku maintenance:off --app {} '.format(HEROKU_APP_NAME))


@task
def transfer_database_from_production(stage='test', clean=True):
    _transfer_database_from_production(stage, clean)


@task
def list_stages():
    """This is put here to test the exact same code in django as in set_stages.  In  one it seems to work
    and another to fail."""
    print('Hi from list_stages in django')
    try:
        stages = env['stages']
        print('List of stages')
        print(stages)
        for stage_name, stage in stages.items():
            try:
                comment = stage['comment']
            except KeyError:
                comment = ''
            print(f'{stage_name} - {comment}')
    except KeyError:
        for k, v in env:
            if k.lower() == 'stages':
                print("env['{f}'] has been set but should probably be 'stages'")
        print("env['stages'] has not been set.")
