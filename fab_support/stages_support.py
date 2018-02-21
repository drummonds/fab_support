# -*- coding: utf-8 -*-
"""stages_support
These are functions
"""
from fabric.api import env, task


@task
def list_stages():
    print('Hi from list_stages')
    try:
        stages = env['stages']
        print('List of stages')
        print(stages)
        for stage_name, stage in stages.items():
            try:
                comment = stage['comment']
            except KeyError:
                comment = ''
            print(f'{stage_name} - {comment}')
    except KeyError:
        for k, v in env:
            if k.lower() == 'stages':
                print("env['{f}'] has been set but should probably be 'stages'")
        print("env['stages'] has not been set.")


__all__ = []
