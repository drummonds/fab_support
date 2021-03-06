=====
Usage
=====


To use fab_support in a project add:

.. code-block:: python

    import fab_support

You will then need a fabfile.py like this:

.. code-block:: python

    from fabric.api import env
    import os
    import time


    import fab_support


    # Operating System Environment variables have precedence over variables defined in the .env file,
    # that is to say variables from the .env files will only be used if not defined
    # as environment variables.
    # Load operating system environment variables and then prepare to use them
    os_env = environ.Env()
    env_file = '.env'
    print('Loading : {}  See {} for more info'.format(env_file, __name__))
    os_env.read_env(env_file)


    # Definition of different environments to deploy to
    env['stages'] = {
        'local': {
            'comment': 'FAC Galleria local version',
            'ENV': {
                'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY_LOCAL'),
            },
            'GIT_BRANCH': 'test'
        },
        'uat': {
            'comment' : 'www.drummonds.net UAT',
            'ENV': {
                'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY_LOCAL'), # same as local
            },
            'DJANGO_SETTINGS_MODULE' : 'drummonds_net.settings.production',  # UAT same as production
            'HEROKU_APP_NAME' : 'drummonds-uat',
            'HEROKU_PROD_APP_NAME': 'drummonds-prod',
            'HEROKU_POSTGRES_TYPE' : 'hobby-basic',  # Need more than 10,000 rows allows to 10M rows but costs $9 a month
            'PRODUCTION_URL' : 'uat.drummonds.net',
            'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY'),
            'DJANGO_ALLOWED_HOSTS' : '.herokuapp.com,.drummonds.net',
            'DJANGO_SENTRY_DSN' : 'https://b1a_very:_secrete6b34d18@sentry.io/1170320',
            'GIT_BRANCH' : 'uat'
        },
        'prod': {
            'comment' : 'www.drummonds.net production',
            'ENV': {
                'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY_PROD'),
            },
            'DJANGO_SETTINGS_MODULE' : 'drummonds_net.settings.production',  # UAT same as production
            'HEROKU_APP_NAME' : 'drummonds-prod',
            'HEROKU_POSTGRES_TYPE' : 'hobby-basic',  # Need more than 10,000 rows allows to 10M rows but costs $9 a month
            'PRODUCTION_URL' : 'www.drummonds.net',
            'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY'),
            'DJANGO_ALLOWED_HOSTS' : '.herokuapp.com,.drummonds.net',
            'DJANGO_SENTRY_DSN' : 'https://b1a_very:_secrete6b34d18@sentry.io@sentry.io/1125110',
            'GIT_BRANCH' : 'master'
        },
    }


------
Stages
------
A stage encapsulates all the deployement characteristics that you need to deploy it.
These will typically include the following:

- *prod* production
- *uat* user acceptance test
- *dev* development

You are free to use any names for the stagies, however fab_support has some special cases.

~~~~~~~~~~
prod stage
~~~~~~~~~~
This stage is the production and so some tasks are made more difficult.
eg to kill the production stage you will normally need the command:

`fab kill_app:prod,safety_on=False`

Without the safety_on parameter it will fail

-------------------------------
General variables env['stage']
-------------------------------

Each stage is defined as a dictionary which has general variables stored at env['stage'].

The documentation breaks down the general definitions here (those that have a meaning in fab_support) and any
environment variables that have a special meaning in the next section.

======================== ======================== ===============================================================
Name                     Default                  Comments
======================== ======================== ===============================================================
comment                                            Identifies which stage this is - used internally eg fab fab_support.list_stages
FS_PLATFORM              heroku                    Which platform is being used eg heroku, dokku
GIT_BRANCH               master                    Which GIT branch to use when building deployment, Required for Heroku deployement when you want to deploy a different branch than master [#git]_.
GIT_PUSH                 *''*                      For specialised GIT push eg using a subtree 'git subtree push --prefix tests/demo_django_postgres heroku master'
GIT_PUSH_DIR             '.'                       Local directory to run git push from eg '../..'
HEROKU_APP_NAME          fab-support-test-app      Name must start with a letter and can only contain lowercase letters, numbers, and dashes. The production name should end in `prod` for additional protection [#herokuappname]_.
HEROKU_PROD_APP_NAME     fab-support-app-prod      Used to identify where to copy the production data from.  Essential for all builds.
HEROKU_OLD_PROD_APP_NAME fab-support-app-old_prod  Name of production (prod)  after promoting uat to prod.
HEROKU_POSTGRES_TYPE     hobby-dev                 free to 10K rows, hobby-basic allows to 10M rows but costs $9 a month
PRODUCTION_URL           *''*                      This is where the production URL should be hosted. empty string if no remote URL [#productionurl]_.
USES_CELERY              False                     If True then will set up on Heroku a scaling worker

======================== ======================== ===============================================================

.. [#git] Heroku uses the local git repository to push from by default. So GIT_BRANCH will be the branch in the local repository
.. [#productionurl] This controls the heroku routing layer which is external to the Django routing layer.  The
    DJANGO_ALLOWED_HOSTS is internal to the Django application and must also match the URL
.. [#herokuappname] This name must be globally distinct for heroku.
.. [#djangosettings] Heroku needs to know what the settings module is and so the name is not passed like a simple
    environment variable.


-----------------------------------------------------
Environment variables env['stages']['stage_x']['ENV']
-----------------------------------------------------

These are the variables that are set in the .env and are carried through to the development environments.  stage_x might
be `uat` or `prod` etc.  For heroku this will then involve the commmand line command like this
`heroku config:set DJANGO_SECRET=very_secret`.

A common pattern is to use a single .env file to store all the secrets and then to use this dictionary to allocate
the secrets to the same environment variable in different stages eg:

.. code-block:: python

    # Not a complete file but for illustration
    env['stages'] = {
        'local': {
            'ENV': {
                'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY_LOCAL'),
            },
        },
        'uat': {
            'ENV': {
                'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY_UAT'),
            },
        },
        'prod': {
            'ENV': {
                'DJANGO_SECRET_KEY' : os.getenv('DJANGO_SECRET_KEY_PROD'),
            },
        },
    }

If an environment variable is listed here it is because fab_support provides a default or takes some other action
with it.

======================== ========================  ===============================================================
Name                     Default                   Comments
======================== ========================  ===============================================================
DJANGO_SETTINGS_MODULE   {{app_name}}              Two scoops config.settings.test or config.settings.production [#djangosettings]_.
DJANGO_ALLOWED_HOSTS     Set                       Will by default allow the app name setup.  See `DJANGO_ALLOWED_HOSTS`_ for more details.
PYTHONHASHSEED           random                    Heroku default
======================== ========================  ===============================================================


--------------------
DJANGO_ALLOWED_HOSTS
--------------------

This pattern was defined by Python django cookiecutter project and is the definition of a environment variable so
that [`ALLOWED_HOSTS`]_ which is a standard Django setting.  Then in the settings file you would have code like this:

.. code:: python

    ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['{{ cookiecutter.domain_name }}'])

Defaults by application type.

======================== ========================
Application              Default
======================== ========================
Heroku                   f'{HEROKU_APP_NAME}.herokuapp.com'
======================== ========================

If you are using an external DNS record to redirection eg via CNAME to the internal Heroku name
then you need to tell fab_support and Heroku that this is happening.
The management of the external domain name is currently out of scope.  However there
should be a DNS record of this type:

.. code:: text

    test.drummonds.net.        CNAME  fab_support_test_prod.herokuapp.com.

.. _`ALLOWED_HOSTS`: https://docs.djangoproject.com/en/2.0/ref/settings/


------
Fabric
------

Fabric version 1 went through a long rewrite into version 2, one of the benefits was supporting Python 3.  In the
 meantime the original Version 1 Fabric was ported to Python 3 as a rewrite.  This is the version that is currently
 used.

