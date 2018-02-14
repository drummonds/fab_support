# fab_support


.. image:: https://img.shields.io/pypi/v/fab_support.svg
        :target: https://pypi.python.org/pypi/fab_support

.. image:: https://img.shields.io/travis/drummonds/fab_support.svg
        :target: https://travis-ci.org/drummonds/fab_support

.. image:: https://readthedocs.org/projects/fab-support/badge/?version=latest
        :target: https://fab-support.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/drummonds/fab_support/shield.svg
     :target: https://pyup.io/repos/github/drummonds/fab_support/
     :alt: Updates


Code to implement staging in Fabric and recipes for using that staging for pelican deployments and Django to Heroku.
It supports a local .env file importing for storing secrets that you don't want to store in git.

In the root fabfile create a dictionary like this which documents how to deploy each stage

STAGES = {
    'localhost': {
        'comment': 'Local build and serving from output directory',
        'destination': '',
        'copy_method': copy_null,
    },
    'harddisk': {
        'comment': 'For serving locally on this computer in another directory. ',
        'destination': 'C:/Sites/www.drummond.info',
        'copy_method': copy_file,
    },
    'production': {
        'destination': 'W:/www.drummond.info',
        'copy_method': copy_file,
    },
}

## Stages
I have create a fab-support.py which does the heavy lifting.  In the root fabfile create a dictionary like this which
documents how to deploy each stage:

```python
# Definition of different environments to deploy to
set_stages (globals(), {
    'localsite': {
        'comment': 'stage: For serving locally on this computer via mongoose. ',
        'config_file': 'local_conf.py',
        'destination': 'C:/Sites/local.drummond.info',
        'copy_method': copy_file,
        'SITEURL': 'http://localhost:8042',
    },
    'production': {
        'comment': 'stage: For serving on local file server',
        'destination': '//10.0.0.1/web/www.drummond.info',
        'config_file': 'local_conf.py',
        'copy_method': copy_file,
        'SITEURL': 'http://www.drummond.info',
},
})
```

Then the deployment by Pelican is pretty standardised eg build deploy and you have commands such as:

`fab localsite deploy`

I think it was inspired by [Breyten Ernsting].  I copied the idea and then elaborated.


[Breyten Ernsting]: http://yerb.net/blog/2014/03/03/multiple-environments-for-deployment-using-fabric/

* Free software: MIT license
* Documentation: https://fab-support.readthedocs.io.

# Settings
These are the variables that are set inthe .env and are carried through to the development environments

## Django settings

Name | Default | Comments
-----|---------|---------
DJANGO_SETTINGS_MODULE| {{app_name}} | Two sccopes config.settings.test or config.settings.production, 


# Heroku

Name | Default | Comments
-----|---------|---------
HEROKU_APP_NAME | fab-support-test-app | Name must start with a letter and can only contain lowercase letters, numbers, and dashes. The production name should end in `prod` for additional protection.
HEROKU_POSTGRES_TYPE | hobby-dev | free to 10K rows, hobby_basic allows to 10M rows 

## Features
--------
Runs on Windows.  If it is getting to complex then it should probably be ported to Ansible or Salt.

### TODO
Clean up importing

## Levels of fabfile in this module
In this module I use three levels of fabfile.py:

- At the project root
- at the /tests root
- at a test/demo level

### Project level fabfile
This is used to do work on the distribution:

- Make deocumentation
- build wheels
- deploy wheels to the package manager

### At the tests level
This is used to run local commands.  Often the commands will be run from the test fab file level and then `lcd` to the
demo level.

### AT the tests/demo level
This is a model fabric file- however it is not like a normal one in that fab_support is not installed in the environment
and in fact is located at `../../fab_support`.

## Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.  Thanks Audrey

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

