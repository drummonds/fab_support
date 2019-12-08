========
Concepts
========

This is an overview of some of the concepts of deployment.

Stages
------

This will be like the following:

- test Testing
- dev Development
- uat User acceptance test
- prod  Production


Platforms
---------

This is where the stage will be deployed :

- Local environment
- Heroku
- dokku

One each platform you may deploy many stages although perhaps unusual to deploy a production stage to
a local environment.

Branches
--------
Typically a stage will be associated with a particular git branch but this can be overided:

+------------+-----------------+
| Stage      | Default Branch  |
+============+=================+
| prod       | master          |
+------------+-----------------+
| uat        | uat             |
+------------+-----------------+

Environment Variables
---------------------
These are secrets which are stored in a .env file in the deployment directory.

It is outside of this scope how you secure and store those .env file. They are clearly not stored inside the .git
repository.


