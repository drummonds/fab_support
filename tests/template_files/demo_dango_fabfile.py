from fabric.api import task

import sys
from pathlib import Path  # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))

# noinspection PyUnresolvedReferences
import fab_support
from fab_support import set_stages
# noinspection PyUnresolvedReferences
from fab_support.django import kill_app, build_app  # Can call directly

# Definition of different environments to deploy to
set_stages(globals(), {
    'test': {
        'comment': 'test version on Heroku',
        'config_file': 'local_conf.py',
    },
})


@task
def test_demo_django_fab_file():
    """A test task to show correct file has been loaded"""
    pass
