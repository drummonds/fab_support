from fabric.api import task, local, lcd
from os import remove, walk
from os.path import join
import re
import sys

from tests.test_utils import remove_tree
from tests.test_django import clean_test_django
from tests.test_django_postgres import clean_setup_postgres
from tests.test_pelican import clean_test_pelican


@task
def clean():
    """remove all build, test, coverage and Python artifacts"""
    clean_build()
    clean_pyc()
    clean_test()
    clean_test_django()
    clean_setup_postgres()
    clean_test_pelican()


def find_and_remove_tree(path, match):
    return path + match


def clean_file(filename):
    try:
        remove(filename)
    except FileNotFoundError:
        pass


def dir_list(path):
    for root, dirs, files in walk(path, topdown=False):
        for name in files:
            print("{}".format(join(root, name)))
        for name in dirs:
            print(join(root, name))


def find_and_remove_file(path, match):
    regex = re.compile(match)
    for root, dirs, files in walk(path, topdown=False):
        for name in files:
            if regex.match(name):
                print("deleting file {}".format(join(root, name)))
        # for name in dirs:
        #    print(join(root, name))


def clean_build():
    """remove build artifacts"""
    remove_tree(("build/", "dist/", ".eggs/"))
    find_and_remove_tree(".", ".egg-info$")
    find_and_remove_file(".", ".egg$")


def clean_pyc():
    """remove Python file artifacts"""
    find_and_remove_file(".", ".pyc$")
    find_and_remove_file(".", ".pyo$")
    find_and_remove_file(".", "~$")
    find_and_remove_file(".", "__pycache__$")


def clean_test():
    """remove test and coverage artifacts"""
    remove_tree(("build/", ".tox/", "htmlcov/"))
    clean_file(".coverage")


@task
def install():
    """Install the package to the active Python's site-packages"""
    clean()
    local("python setup.py install")


@task
def dist():
    """builds source and wheel package"""
    clean()
    local("python setup.py sdist")
    local("python setup.py bdist_wheel")
    dir_list("dist")


@task
def release():
    """package and upload a release"""
    clean()
    local("python setup.py sdist upload")
    local("python setup.py bdist_wheel upload")


@task
def make_docs():
    """Create documentation"""
    with lcd("docs"):
        ## generate Sphinx HTML documentation, including API docs
        try:
            remove("docs/fab_support.rst")
        except FileNotFoundError:
            pass
        try:
            remove("docs/modules.rst")
        except FileNotFoundError:
            pass
        local("sphinx-apidoc -o . ../fab_support")
        # $ (MAKE) - C         docs         clean
        local("make html")
        # $(BROWSER)    docs / _build / html / index.html


@task
def identity():
    """Which version of fabfile am I using"""
    try:
        import fab_support

        version = f"fab_support version {fab_support._version.__version__}"
    except ImportError:
        version = "No fab_support to import"
    print(
        f"Module fabfile {version}"
    )  # Use print rather than exit to make it easier to capture test output
