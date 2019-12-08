"""
Platform support interface for fab_support
This will redirect various tasks to the correct platform to support them
"""
from fabric.api import env

#
import fab_support.heroku as heroku
from fab_support import FabricSupportException


def env_to_platform(stage):
    """
    Given a stage will return the

    :param stage: Which stage is being used eg prod uat
    :return:
    """
    platform = env['stages'][stage]["FS_PLATFORM"]
    if platform in ('heroku',):  # limit for security
        return platform
    else:
        raise FabricSupportException(f'Unknown platform: {platform}')


def env_to_function(stage, my_function_name):
    """
    Given the name of a stage and function will return that function

    :param stage: Which stage is being used eg prod uat
    :return:
    """
    platform = env_to_platform(stage)
    the_module = globals()[platform]  # This is an indirect reference to the module
    func = getattr(the_module, my_function_name)
    return func


def fab_support_function(stage, function_name, **kwargs):
    func = env_to_function(stage, function_name)
    func(stage, **kwargs)

