from distutils.dir_util import copy_tree
from fabric.api import settings, local
from time import sleep
import sys

class FabricSupportException(Exception):
    pass


# Utility functions
# Different methods of deployment
# copy_null eg for running locally from test directory
# noinspection PyUnusedLocal
def copy_null(source, destination):
    pass  # Already there


def copy_file(source, destination):
    copy_tree(source, destination)  # from one file location to another


def repeat_run_local(command, repeats=5, interval=15):
    """
    When you run some commands they fail.  This failure might actually be due to a timing issue. For instance
    trying:

        heroku pg:wait --app {HEROKU_APP_NAME}
        heroku pg:backups:schedule --at 04:00 --app {HEROKU_APP_NAME}

    wait can return before the database is properly prepared.  In this instance it is actually fine to wait a little
    bit and try again.  Clearly you don't want to wait for ever as there may be a real problem.

    command = f'heroku pg:backups:schedule --at 04:00 --app {HEROKU_APP_NAME}'

    .. code:: python

        try:
            local(command)
        except Exception:


    Already promoted as new local('heroku pg:promote DATABASE_URL --app my-app-prod')

    Leaving out and aws and reddis

    :param command: Command to try run as local
    :param repeats: How many times should you repeat the command
    :param interval: How long should the interval be between tyring again (in seconds)
    :return: Nothing / if fails will have a system exit

    """
    for i in range(repeats):
        with settings(abort_exception=FabricSupportException):
            try:
                local(command)
                return  # All good here
            except FabricSupportException:
                print(f'  Sleep and retry command attempt {i+1}')
        sleep(interval)
    # Now we have exhausted the retries and really need to bring this to a quick stop
    sys.exit(f"Retried '{command}' {repeats} times and still failed")


