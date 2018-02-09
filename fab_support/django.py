import datetime as dt
from fabric.api import local, task
from fabric.operations import require
import os
import time


##################################################
# Local utilities
##################################################

def remove_unused_db(env_prefix='uat'):
    """List all databases in use for app, find the main one and remove all the others"""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    data = json.loads(local(f'heroku config --json --app {heroku_app}', capture=True))
    for k,v in data.items():
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v != data['DATABASE_URL']:
                local(f'heroku addons:destroy {k} --app {heroku_app} --confirm {heroku_app}')


def default_db_colour(app_name):
    """Return the default database colour of heroku application"""
    data = json.loads(local('heroku config --json --app {0}'.format(app_name), capture=True))
    result = ''
    for k,v in data.items():
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v == data['DATABASE_URL']:
                return k
    # if no colour found then try the long name in database_url
    # raise Exception(f'No color database names found for app {app_name} - create an extra one and it should be ok.')
    return data['DATABASE_URL']
def set_environment_variables(env_prefix):
    if env_prefix == 'test':
        settings = 'develop'
    else:
        settings = 'production'
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    local(f"heroku config:set DJANGO_SETTINGS_MODULE=config.settings.{settings} --app {heroku_app}")
    local('heroku config:set PYTHONHASHSEED=random --app {}"'.format(heroku_app))
    local('heroku config:set DJANGO_ALLOWED_HOSTS="{1}.herokuapp.com" --app {1}'.
          format(os.environ['DJANGO_ALLOWED_HOSTS'], heroku_app))
    for config in ( 'DJANGO_SECRET_KEY', 'DJANGO_ADMIN_URL'
        ,'DJANGO_AWS_ACCESS_KEY_ID', 'DJANGO_AWS_SECRET_ACCESS_KEY', 'DJANGO_AWS_STORAGE_BUCKET_NAME'
        ,'DJANGO_MAILGUN_API_KEY', 'DJANGO_SERVER_EMAIL', 'MAILGUN_SENDER_DOMAIN'
        ,'DJANGO_ACCOUNT_ALLOW_REGISTRATION', 'DJANGO_SENTRY_DSN'
        ,'XERO_CONSUMER_SECRET', 'XERO_CONSUMER_KEY'):
        local('heroku config:set {}={} --app {}'.format(config, os.environ[config], heroku_app))


def raw_update_app(env_prefix='uat', branch='master'):
    """Update of app to latest version"""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    # Put the heroku app in maintenance move
    set_environment_variables(env_prefix)  # In case anything has changed
    # connect git to the correct remote repository
    local('heroku git:remote -a {}'.format(heroku_app))
    # Need to push the branch in git to the master branch in the remote heroku repository
    local(f'git push heroku {branch}:master')
    # Don't need to scale workers down as not using eg heroku ps:scale worker=0
    # Will add guvscale to spin workers up and down from 0
    local(f'heroku ps:scale worker=1 -a {heroku_app}')
    # Have used performance web=standard-1x and worker=standard-2x but adjusted app to used less memory
    #local(f'heroku ps:resize web=standard-1x -a {heroku_app}')  # Resize web to be compatible with performance workers
    #local(f'heroku ps:resize worker=standard-2x -a {heroku_app}')  # Resize workers
    # makemigrations should be run locally and the results checked into git
    local('heroku run "yes \'yes\' | python manage.py migrate"')  # Force deletion of stale content types


def _create_newbuild(env_prefix='test', branch='master'):
    """This builds the database and waits for it be ready.  It is is safe to run and won't
    destroy any existing infrastructure."""
    # subprocess.call('heroku create --app {} --region eu'.format(staging), shell=True)
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    # local('heroku create --app {} --region eu'.format(heroku_app))  # Old style
    local('heroku create {0} --buildpack https://github.com/heroku/heroku-buildpack-python --region eu'
          .format(heroku_app))
    # This is where we create the database.  The type of database can range from hobby-dev for small
    # free access to standard for production quality docs
    local('heroku addons:create heroku-postgresql:hobby-basic --app {0}'.format(heroku_app))
    local(f'heroku addons:create cloudamqp:lemur --app {heroku_app}')
    local(f'heroku addons:create papertrail:choklad --app {heroku_app}')
    # Add guvscale processing to allow celery queue to be at zero
    # guvscale seems not to work in beta
    # local(f'heroku addons:create guvscale --app {heroku_app}')
    try:
        local(f'heroku plugins:install heroku-cli-oauth')  # installed in local toolbelt not on app
    except:
        print('Probably already installed')
    # Now need to create a token and add to guvscale
    # Does'nt work
    #data = json.loads(local(
    #    f'heroku authorizations:create --json --description "GuvScale" -s write,read-protected --app {heroku_app}',
    #    capture=True))
    #print(f'Data for guvscale = :{data}')
    # Load guvscale cli tool (may already be installed)
    try:
        local(f'heroku plugins:install heroku-guvscale')  # installed in local toolbelt not on app
    except:
        print('Probably already installed')
    # start of configuring guvscale to autoscale
    # local(f'heroku guvscale:getconfig --app {heroku_app}')
    # set database backup schedule
    local('heroku pg:wait --app {0}'.format(heroku_app))  # It takes some time for DB so wait for it
    local('heroku pg:backups:schedule --at 04:00 --app {0}'.format(heroku_app))
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app bene-prod')
    # Leaving out and aws and reddis
    raw_update_app(env_prefix, branch=branch)
    local('heroku run python manage.py check --deploy') # make sure all ok
    su_name = os.environ['SUPERUSER_NAME']
    su_email = os.environ['SUPERUSER_EMAIL']
    su_password = os.environ['SUPERUSER_PASSWORD']
    cmd = ('heroku run "echo \'from django.contrib.auth import get_user_model; User = get_user_model(); '
        + f'User.objects.filter(email="""{su_email}""", is_superuser=True).delete(); '
        + f'User.objects.create_superuser("""{su_name}""", """{su_email}""", """{su_password}""")\' '
        + f' | python manage.py shell"' )
    local(cmd)


@task
def create_newbuild(env_prefix='test', branch='master'):
    _create_newbuild(env_prefix, branch)

def _kill_app(env_prefix, safety_on=True):
    """see _kill app"""
    if not (env_prefix == 'prod' and safety_on):  # Safety check - remove when you need to
        heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
        local('heroku destroy {0} --confirm {0}'.format(heroku_app))


@task
def kill_app(env_prefix, safety_on=True):
    """Kill app notice that to the syntax for the production version is:
    fab kill_app:prod,safety_on=False"""
    require('stage')
    _kill_app(env_prefix, safety_on)


@task
def build_uat():
    """Build a new uat environments"""
    build_app()


@task
def build_app(env_prefix='uat'):
    """Build a test environment. Default is uat.
    So fab build_app  is equivalent to fab build_app:uat  and to fab build_app:env_prefix=uat
    so can build a test branch with:
        fab build_app:env_prefix=test"""
    start_time = time.time()
    try:
        _kill_app(env_prefix)
    except SystemExit:
        if env_prefix != 'prod':
            pass # ignore errors in case original does not exist
        else:
            raise Exception('Must stop if an error when deleting a production database.')
    _create_newbuild(env_prefix, branch=env_prefix)
    local(f'fab transfer_database_from_production:{env_prefix}')
    # makemigrations should be run locally and the results checked into git
    # Need to migrate the old database schema from the master production database
    local('heroku run "yes \'yes\' | python manage.py migrate"')  # Force deletion of stale content types
    # Calculate time
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f'Run time = {runtime} Completed at: {dt.datetime.now()}')


def _transfer_database_from_production(env_prefix='test', clean=True):
    """This is usally used for making a copy of the production database for a UAT staging
    or test environment.  It can also be used to upgrade the production environment from one
    database plan to the next. """
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    heroku_app_prod = '{0}-prod'.format(os.environ['HEROKU_PREFIX'])
    # Put the heroku app in maintenance move
    try:
        local('heroku maintenance:on --app {} '.format(heroku_app) )
        colour, db_name = create_new_db(env_prefix)  # color is ?
        # Don't need to scale workers down as not using eg heroku ps:scale worker=0
        local(f'heroku pg:copy {heroku_app_prod}::DATABASE_URL {colour} --app {heroku_app} --confirm {heroku_app}')
        local(f'heroku pg:promote {colour}')
        if clean:
            remove_unused_db(env_prefix)
    finally:
        local('heroku maintenance:off --app {} '.format(heroku_app))


@task
def transfer_database_from_production(env_prefix='test', clean=True):
    _transfer_database_from_production(env_prefix, clean)
