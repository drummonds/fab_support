from shutil import rmtree


def remove_tree(path):
    assert path not in ('c:\\', 'c:', '\\', '/')  # Add safety check
    if isinstance(path, tuple) or isinstance(path, list):
        for this in path:
            remove_tree(this)
    else:
        rmtree(path, ignore_errors=True)
