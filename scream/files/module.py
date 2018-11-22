from .util import File

MODULE = """\
def add_1(i):
    return i + 1
"""

TEST = """\
import unittest

from {package_name}.module import add_1


class ExampleTest(unittest.TestCase):

    def test_example(self):
        result = add_1(1)
        self.assertTrue(result == 2)
"""


class ModuleExample(File):
    def __init__(self):
        super(ModuleExample, self).__init__(
            'module.py',
            MODULE
        )


class TestExample(File):
    def __init__(self, package_name):
        self.package_name = package_name

        super(TestExample, self).__init__(
            'test_module.py',
            TEST.format(package_name=package_name)
        )
