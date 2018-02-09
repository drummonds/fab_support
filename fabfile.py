from fabric.api import task, local
from os import remove, walk
from os.path import join
import re
from shutil import rmtree


@task
def clean():
    """remove all build, test, coverage and Python artifacts"""
    clean_build()
    clean_pyc()
    clean_test()


def remove_tree(path):
    assert path not in ('c:\\', 'c:', '\\', '/')  # Add safety check
    if isinstance(path, tuple) or isinstance(path, list):
        for this in path:
            remove_tree(this)
    else:
        rmtree(path, ignore_errors=True)


def find_and_remove_tree(path, match):
    return path+match


def clean_file(filename):
    try:
        remove(filename)
    except FileNotFoundError:
        pass


def dir_list(path):
    for root, dirs, files in walk(path, topdown=False):
        for name in files:
            print('{}'.format(join(root, name)))
        for name in dirs:
            print(join(root, name))


def find_and_remove_file(path, match):
    regex = re.compile(match)
    for root, dirs, files in walk(path, topdown=False):
        for name in files:
            if regex.match(name):
                print('deleting file {}'.format(join(root, name)))
        # for name in dirs:
        #    print(join(root, name))


def clean_build():
    """remove build artifacts"""
    remove_tree(('build/', 'dist/', '.eggs/'))
    find_and_remove_tree('.', '.egg-info$')
    find_and_remove_file('.', '.egg$')


def clean_test():
    """remove build artifacts"""
    remove_tree(('tests/pelican',))


def clean_pyc():
    """remove Python file artifacts"""
    find_and_remove_file('.', '.pyc$')
    find_and_remove_file('.', '.pyo$')
    find_and_remove_file('.', '~$')
    find_and_remove_file('.', '__pycache__$')


def clean_test():
    """remove test and coverage artifacts"""
    remove_tree(('build/', '.tox/', 'htmlcov/'))
    clean_file('.coverage')


@task
def install():
    """Install the package to the active Python's site-packages"""
    clean()
    local('python setup.py install')


@task
def dist():
    """builds source and wheel package"""
    clean()
    local('python setup.py sdist')
    local('python setup.py bdist_wheel')
    dir_list('dist')


@task
def release():
    """package and upload a release"""
    clean()
    local('python setup.py sdist upload')
    local('python setup.py bdist_wheel upload')
