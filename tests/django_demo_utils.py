import os
from pathlib import Path
import shutil

from fabric.api import local, lcd, settings
"""This requires git and pipenv to work but no deployment application"""

def clean_setup(platform = None):
    # Try and remove demo_django directory
    # Work out where it is being called from
    if os.path.isdir("tests"):
        my_path = "tests/demo_django"
        my_path2 = "tests/"
    elif os.path.isdir("template_files"):
        my_path = "demo_django"
        my_path2 = ""
    else:
        raise Exception
    if Path(my_path).exists():
        print(f'Deleting path {my_path}')
        if platform:
            with lcd(my_path):
                try:
                    # Calling fabric in local test directory
                    # This is to kill the OLD app, the new app which will be created will have a new name
                    local(f"fab kill_app:demo_{platform}", capture=True)
                except SystemExit:
                    pass
        # bodge to get .git file delete keeps giving a PermissionError after testing about a git file
        # The file is probably open with node
        try:
            with settings(warn_only=True):
                with lcd(my_path):
                    local("del /F /S /Q /A .git", capture=True)  # Get rid of output
        except (FileNotFoundError, SystemExit):
            pass
        with lcd(my_path2):
            try:
                shutil.rmtree(my_path2 + "demo_django")
            except FileNotFoundError:
                pass
    else:
        print(f'Path {my_path} already deleted')


def django_demo_setup(platform=None):
    """Create a test django project"""

    def copy_local_file(source, destination, suffix=""):
        """Copy a local template file to the demo_django directory """
        local(
            "copy "
            + str(Path("template_files") / source)
            + " "
            + str(Path("demo_django") / destination)
            + suffix
        )

    clean_setup(platform=platform)
    local("django-admin startproject demo_django")
    # TODO convert paths to windows and linux
    copy_local_file("demo_django_fabfile.py", "fabfile.py")  # Automation tasks
    copy_local_file("demo_django.env", ".env")  # Secrets managment
    copy_local_file(
        "demo_django_Procfile", "Procfile"
    )  # Workers required for Heroku/dokku
    copy_local_file("demo_Pipfile", "Pipfile")  # Python env
    copy_local_file("demo_Pipfile.lock", "Pipfile.lock")  # Environment lock
    copy_local_file(
        "demo_django_settings.py", "demo_django/settings.py", suffix=" /Y"
    )  # Need to customise
    # for collect statics (alternative would be to ignore collect static)
    # Setup a git for Heroku to use to deploy demo_django
    local("git init demo_django")
    with lcd("demo_django"):
        local(
            "mkdir static"
        )  # Heroku needs a place to put static files in collectstatic and won't create it.
        local(
            "copy ..\\template_files\\demo_django_fabfile.py static\\fabfile.py"
        )  # To make git recognise it
        local("git add .")
        local("git commit -m 'start'")
