"""
Thanks https://stackoverflow.com/questions/13761697/how-to-access-the-unittest-mainverbosity-setting-in-a-unittest-testcase
I can't believe this is the simplest way.
"""
import inspect
import unittest

def unittest_verbosity():
    """Return the verbosity setting of the currently running unittest
    program, or 0 if none is running.

    """
    frame = inspect.currentframe()
    while frame:
        self = frame.f_locals.get('self')
        if isinstance(self, unittest.TestProgram):
            return self.verbosity
        frame = frame.f_back
    return 0

def verbose():
    return True  # TODO debug unittest_verbosity() > 2
