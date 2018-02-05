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

## Stages
I have create a fab-support.py which does the heavy lifting.  Then in your fabric file you have a dictionary:

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


## Features
--------

* TODO

## Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.  Thanks Audrey

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

