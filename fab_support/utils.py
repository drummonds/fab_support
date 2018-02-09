from distutils.dir_util import copy_tree


class FabricSupportException(Exception):
    pass


# Utility functions
# Different methods of deployment
# copy_null eg for running locally from test directory
# noinspection PyUnusedLocal
def copy_null(source, destination):
    pass  # Already there


def copy_file(source, destination):
    copy_tree(source, destination)  # from one file location to another
