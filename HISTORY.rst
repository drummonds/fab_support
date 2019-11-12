History
=======

0.3.0 (2019-11-12)
------------------
This is actually a series of major breaking changes.

* Changing from .env to config.json for storage of secrets
* Changing from predefined tasks to methods which can be used
* Implementation of dokku alongside Heroku as a deployment platform
* Changing from requirements.txt to pipenv for managing dependencies

.env to config.json
~~~~~~~~~~~~~~~~~~~
This change is inspired by zappa which has a configuration file zappa.json.  Each environment has
mostly the same list of environment variables (obviously with different values).  A hierachical
data structure is a nice way to store these.

Predefined tasks to methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The previous methods meant that including tasks created lots of verbiage when you did `fab --list`
In order to simplify the output I am now providing tools that need to be selected for your
particular use case.

Support for dokku
~~~~~~~~~~~~~~~~~
I have started to use dokku for lower cost.  Heroku can still scale to a larger intances.

requirements.txt to pipenv
~~~~~~~~~~~~~~~~~~~~~~~~~~
I am using pipenv quite happily and find it easier to bundle up the dependencies and is quite widely
supported eg on PyCharm.

0.2.1 (2018-05-11)
------------------
* Updating pelican commands to the parameter method of passing stage.

Note tests were failing to a non obvious cause.  This was Heroku CLI needed updating to the latest version.
I manually upgraded.

0.2.0 (2018-04-20)
------------------
* Change the way environment variables are passed through.

In version 0.1 only the following variables were considered env variables:

'DJANGO_SECRET_KEY', 'DJANGO_ADMIN_URL', 'DJANGO_AWS_ACCESS_KEY_ID', 'DJANGO_AWS_SECRET_ACCESS_KEY',
'DJANGO_AWS_STORAGE_BUCKET_NAME', 'DJANGO_MAILGUN_API_KEY', 'DJANGO_SERVER_EMAIL', 'MAILGUN_SENDER_DOMAIN',
'DJANGO_ACCOUNT_ALLOW_REGISTRATION', 'DJANGO_SENTRY_DSN', 'XERO_CONSUMER_SECRET', 'XERO_CONSUMER_KEY'

Now there is an 'ENV' list of variables that allows any variables to be passed through and also for them to
renamed on the way from the file .env

0.1.0 (2018-02-04)
------------------

* First release on PyPI.
