=======
History
=======

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
