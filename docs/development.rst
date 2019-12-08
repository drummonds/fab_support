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
