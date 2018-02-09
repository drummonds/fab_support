from fabric.api import task

import fab_support


@task
def test_fab_file():
    """A test task to show correct file has been loaded"""
