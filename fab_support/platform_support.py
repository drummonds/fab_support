"""
Platform support interface for fab_support
This will redirect various tasks to the correct platform to support them
"""
from fabric.api import env

#
import fab_support
from fab_support import FabricSupportException


def env_to_platform(stage):
    """
    Given a stage will return the

    :param stage: Which stage is being used eg prod uat
    :return:
    """
    platform = env["stages"][stage]["FS_PLATFORM"]
    if platform in ("heroku", "dokku"):  # limit for security
        return platform
    else:
        raise FabricSupportException(f"Unknown platform: {platform}")


def env_to_function(stage, my_function_name):
    """
    Given the name of a stage and function will return that function

    :param stage: Which stage is being used eg prod uat
    :return:
    """
    platform = env_to_platform(stage)
    fs = fab_support
    func = getattr(getattr(fs, platform), my_function_name)
    return func


def fab_support_function(stage, function_name, **kwargs):
    """
    Given a stage and a function name will indirectly call that function and pass the stage to it.
    The function must have a parameter as stage.

    :param stage: Which stage is being used eg prod uat
    :param function_name: The name of the function to be called in the module defined by the platform variable.
    :return:
    """
    func = env_to_function(stage, function_name)
    return func(stage, **kwargs)
