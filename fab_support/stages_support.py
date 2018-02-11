# -*- coding: utf-8 -*-
"""stages_support
These are functions
"""
import os
import sys
import time

from fabric.api import env, task
from fabric.utils import abort, warn


# Definition of stages to be overridden
STAGES = {}


# Conversion of stage settings to environment variables
def stage_set(stage_name='test'):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)
    try:
        if env['SITEURL']:
            os.environ['SITEURL'] = env['SITEURL']
        else:
            warn("Setting SITEURL to null string doesn't work for Pelican. Changed to .")
            os.environ['SITEURL'] = '.'  # Must be defined
    except KeyError:
        warn('Pelican requires SITEURL to be set.')
        os.environ['SITEURL'] = '.'  # Must be defined


# noinspection PyUnusedLocal
def create_a_function(stage_name, *args, **kwargs):
    """Create a simple Task function suitable for marking a stage.
    This just switches the staging environment."""

    # noinspection PyUnusedLocal,PyShadowingNames
    def function_template(*args, **kwargs):
        if not hasattr(env, 'stage'):
            stage_set(stage_name)
        else:
            abort(f'Have already set the environment to {env.stage}. Can only set once.')

    return function_template


# Conversion of enumerated stages to functions
def set_stages(namespace, stages):  # namespace, stage_dict):
    """Make each name in stage_dict a top level fabric task"""
    global STAGES
    STAGES = stages
    # namespace = globals()
    this_module = sys.modules[__name__]
    for stage_name, value in STAGES.items():  # stage_dict.items():
        f = create_a_function(stage_name)
        # task description
        try:
            f.__doc__ = STAGES[stage_name]['comment']
        except KeyError:
            f.__doc__ = f'{stage_name} is a deployment location'
        # task name
        task_name = f'{stage_name}'
        # call task decorator as function to generate WrappedCallableTask
        wrapper = task(name=task_name)
        rand = '%d' % (time.time() * 100000)
        namespace['task_%s_%s' % (task_name, rand)] = wrapper(f)
        # Try putting the functions locally as well
        setattr(this_module, stage_name, f)


@task
def list_stages():
    for s in STAGES:
        print(s)
