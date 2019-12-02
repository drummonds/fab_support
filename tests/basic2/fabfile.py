from fabric.api import task, env

# Need to modify path so fab_support is found
# This is only needed to run test fabfile's in a test directory
import sys
from pathlib import Path  # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))

# noinspection PyUnresolvedReferences
import fab_support

env['stages'] = {
    'demo': {
        'comment': 'Simplest demo project',
    },
    'production': {
        'comment': 'Production project tag:456 for regex match',
    },
    }


@task
def test_demo2_fab_file():
    """A test task to show correct file has been loaded"""
    pass


@task
def list_stages():
    """Showing use of a helper function"""
    return fab_support.list_stages()


@task
def identity():
    """Which version of fabfile am I using"""
    try:
        import fab_support
        version = f"fab_support version {fab_support._version.__version__}"
    except ImportError:
        version = 'No fab_support to import'
    print(f"tests/basic2 fabfile {version}")
