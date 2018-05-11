import datetime as dt
from fabric.api import env, local, task, lcd, settings
import json
import os
import re
import time
from time import sleep

from .heroku_utils import first_colour_database
from .utils import repeat_run_local, FabricSupportException

# Global environment variables See documentation
HEROKU_APP_NAME = 'fab-support-app-test'  # name of this stages Heroku app
HEROKU_PROD_APP_NAME = 'fab-support-app-prod'  # Name of Heroku app which is production, ie source of data
HEROKU_OLD_PROD_APP_NAME = 'fab-support-app-old-prod'  # Name of heroku app to save production to
PRODUCTION_URL = ''
HEROKU_POSTGRES_TYPE = 'hobby-dev'
GIT_PUSH = ''  # Default to false
GIT_PUSH_DIR = '.'  #
GIT_BRANCH = 'master'
USES_CELERY = False


##################################################
# Local utilities
##################################################

def remove_unused_db():
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
    for k, v in data.items():
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v == data['DATABASE_URL']:
                return k
    # if no colour found then try the long name in database_url
    # raise Exception(f'No color database names found for app {app_name} - create an extra one and it should be ok.')
    return data['DATABASE_URL']


def set_heroku_environment_variables(stage):
    """This sets all the environment variables that a Django recipe needs."""
    # TODO deal with no 'ENV'
    env_dict = env['stages'][stage]['ENV']  # Should be a dictionary
    # Set all the variables you need
    for key, value in env_dict.items():
        local('heroku config:set {}={} --app {}'.format(key, value, HEROKU_APP_NAME))
    # Setup defaults for some ENV variables if have not been setup
    if 'DJANGO_ALLOWED_HOSTS' not in env_dict:
        allowed_hosts = f'{HEROKU_APP_NAME}.herokuapp.com'
        local(f'heroku config:set DJANGO_ALLOWED_HOSTS="{allowed_hosts}" --app {HEROKU_APP_NAME}')
    if 'DJANGO_SETTINGS_MODULE' not in env_dict:
        local(f'heroku config:set DJANGO_SETTINGS_MODULE=production --app {HEROKU_APP_NAME}')
    if 'PYTHONHASHSEED' not in env_dict:
        local(f'heroku config:set PYTHONHASHSEED=random --app {HEROKU_APP_NAME}')


def raw_update_app(stage):
    """Update of app to latest version"""
    # Put the heroku app in maintenance mode TODO
    set_heroku_environment_variables(stage)  # In case anything has changed
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
        if plug_in not in plugin_dict:
            local(f'heroku plugins:install {plug_in}')  # installed in local toolbelt not on app
            # If it fails then it really is a failure not just it has already been installed.
    return True  # Got to end and all installed
    # print(f'|{results}|')


# #############
def _create_newbuild(stage):
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
    repeat_run_local(f'heroku pg:wait --app {HEROKU_APP_NAME}')  # It takes some time for DB so wait for it
    # When wait returns the database is not necessarily completely finished preparing itself.  So the next
    # command could fail (and did on testing on v0.1.6)
    repeat_run_local(f'heroku pg:backups:schedule --at 04:00 --app {HEROKU_APP_NAME}')
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app my-app-prod')
    # Leaving out and aws and reddis
    raw_update_app(stage)
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
    for global_env in ('HEROKU_APP_NAME', 'HEROKU_PROD_APP_NAME', 'HEROKU_OLD_PROD_APP_NAME',
                       'PRODUCTION_URL',
                       'HEROKU_POSTGRES_TYPE',
                       'USES_CELERY',
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
    _create_newbuild(stage)


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
    get_global_environment_variables(stage)
    if not (is_production() and not safety_on):
        _kill_app()


@task
def build_uat():
    """Build a new uat environments"""
    build_app('uat')


def _build_app(stage='uat'):
    """Build a test environment. Default is uat.
    So fab build_app  is equivalent to fab build_app:uat  and to fab build_app:stage=uat
    so can build a test branch with:
        fab build_app:stage=test"""
    try:
        _kill_app()
    except SystemExit:
        if stage != 'prod':
            pass  # ignore errors in case original does not exist
        else:
            raise Exception('Must stop if an error when deleting a production database as now the only working instance is UAT.')
    _create_newbuild(stage)
    _transfer_database_from_production(stage)
    # makemigrations should be run locally and the results checked into git
    # Need to migrate the old database schema from the master production database
    local('heroku run "yes \'yes\' | python manage.py migrate"')  # Force deletion of stale content types


@task
def build_app(stage='uat'):
    start_time = time.time()
    get_global_environment_variables(stage)
    _build_app(stage)
    # Calculate time
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f'Run time = {runtime} Completed at: {dt.datetime.now()}')


def _create_new_db():
    """Just creates an extra new database for this instance."""
    # Put the heroku app in maintenance move
    m = local(f'heroku addons:create heroku-postgresql:{HEROKU_POSTGRES_TYPE} --app {HEROKU_APP_NAME}', capture=True)
    repeat_run_local('heroku pg:wait')  # It takes some time for DB so wait for it
    # There should now be 2 database
    return first_colour_database(app=HEROKU_APP_NAME)


@task
def create_new_db(stage='uat'):
    get_global_environment_variables(stage)
    return _create_new_db()


def _transfer_database_from_production(stage='test', clean=True):
    """This is usually used for making a copy of the production database for a UAT staging
    or test environment.  It can also be used to upgrade the production environment from one
    database plan to the next.
    Method:
    """
    try:
        local('heroku maintenance:on --app {} '.format(HEROKU_APP_NAME))
        db_name, colour = create_new_db(stage)  # colour is ?
        # Don't need to scale workers down as not using eg heroku ps:scale worker=0
        local(
            f'heroku pg:copy {HEROKU_PROD_APP_NAME}::DATABASE_URL {colour} --app {HEROKU_APP_NAME} --confirm {HEROKU_APP_NAME}')
        local(f'heroku pg:promote {colour}')
        if clean:
            remove_unused_db()
    finally:
        local('heroku maintenance:off --app {} '.format(HEROKU_APP_NAME))


@task
def transfer_database_from_production(stage='test', clean=True):
    get_global_environment_variables(stage)
    _transfer_database_from_production(stage, clean)


@task
def list_stages():
    """This is put here to test the exact same code in django as in set_stages.  In  one it seems to work
    and another to fail."""
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


def _promote_uat():
    """
    Promotes a stage typically, uat to production
    Saves old production for safety
    Should work if this is the first promotion ie no production database or if there is a production database.
    TODO require manual override if not uat
    TODO do not run of old_prod exists.  Require manual deletion
    """
    production_exists = True
    with settings(abort_exception=FabricSupportException):
        try:
            local(f'heroku maintenance:on --app {HEROKU_PROD_APP_NAME}')
        except FabricSupportException:
            # Going to assume that there is no production
            production_exists = False
    try:
        if production_exists:
            local(
                f'heroku apps:rename {HEROKU_OLD_PROD_APP_NAME} --app {HEROKU_PROD_APP_NAME}')  # Should fail if already an old_prod
        local(f'heroku apps:rename {HEROKU_PROD_APP_NAME} --app {HEROKU_APP_NAME}')
        if production_exists:
            # Update allowed site
            local(
                f'heroku config:set DJANGO_ALLOWED_HOSTS="{HEROKU_OLD_PROD_APP_NAME}.herokuapp.com" --app {HEROKU_OLD_PROD_APP_NAME}')
            local(
                f'heroku config:set DJANGO_ALLOWED_HOSTS="{HEROKU_PROD_APP_NAME}.herokuapp.com" --app {HEROKU_PROD_APP_NAME}')
            if PRODUCTION_URL:
                # Switch over domains
                local(f'heroku domains:clear --app {HEROKU_OLD_PROD_APP_NAME}')
                local(f'heroku domains:add {PRODUCTION_URL} --app {HEROKU_PROD_APP_NAME}')
    finally:
        if production_exists:
            local(f'heroku maintenance:off --app {HEROKU_PROD_APP_NAME} ')  # Different prod does this matter?


@task
def promote_uat(stage='uat'):
    get_global_environment_variables(stage)
    start_time = time.time()
    _promote_uat()
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f'Run time = {runtime}')
