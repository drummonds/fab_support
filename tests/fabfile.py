import sys
from fabric.api import task


@task
def test_fab_file():
    """A test task to show correct file has been loaded"""


@task
def identity():
    """Which version of fabfile am I using"""
    try:
        import fab_support

        version = f"fab_support version {fab_support._version.__version__}"
    except ImportError:
        version = "No fab_support to import"
    print(f"Test fabfile {version}")
