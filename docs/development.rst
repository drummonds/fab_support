===========
Development
===========

An overview of the development aspects.  This covers the structure and the use of fabric internal

Internal Levels of fabfile in this module
-----------------------------------------
In this module I use three levels of fabfile.py:

- At the project root
- at the /tests root
- at a test/demo level

This can get confusing, however they operate at different levels.  The project is about project operations eg
releasing to fab_support to pypi.

The tests level is then about managing the tests.  Some of these tests use fab support and a fabfile.py which gives you
the third level of nesting.

Project level fabfile
~~~~~~~~~~~~~~~~~~~~~
This is used to do work on the distribution:

- Make documentation
- build wheels
- deploy wheels to the package manager

At the tests level
~~~~~~~~~~~~~~~~~~~~~
This is used to run local commands.  Often the commands will be run from the test fab file level and then `lcd` to the
demo level.

At the tests/demo level
~~~~~~~~~~~~~~~~~~~~~~~
This is a model fabric file- however it is not like a normal one in that fab_support is not installed in the environment
and in fact is located at `../../fab_support`.


----------------------
Rebuilding fab_support
----------------------
From time to time you will need to rebuild fab_support.  As this uses demo projects
these may get out of date and need refreshing to the latest versions.  This is the documentation
to help with that process.

demo_django pipfile change
~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to make the testing process quicker, the pipfile.lock is precompiled by pipenv.
When pipenv changes eg new version of Python, Django you will need to rebuild.

- get a ./tests/demo_django directory  There may be one if a test has failed or else:
    - edit tests.test_django_demo_utils.test_setup_and_teardown to comment out the final
      clean_setup()  (There is another at the begining so the tests will still run but after the
      test has run you will be able to inspect one
- Open a terminal and navigate to ./tests/demo_django directory
- if python version has changed remove the virtual environment with `pipenv --rm`
- update Pipfile.lock with `pipenv update`
- copy the Pipfile.lock to ./tests/template_files/demo_Pipfile.lock
- undo edits to tests.test_django_demo_utils.test_setup_and_teardown if edited at the begining.

--------------------------------
Adding a new deployment strategy
--------------------------------
Currently two strategies are implemented:
    - heroku
    - dokku

When you add a new one you need to do the following:
    - Add a module to fab_support eg like dokku.py or heroku.py
    - update any lists with dokku and heorku in
    - add tests for both basic deployment and with postgres.
