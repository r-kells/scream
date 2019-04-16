from .util import File

TEMPLATE = """\
# When you call `scream deploy` this file is called, if files for this package have changed.
print('No deploy commands set for: {package_name}')
"""


class Deploy(File):
    def __init__(self, package_name):
        super(Deploy, self).__init__(
            'deploy.py',
            TEMPLATE.format(
                package_name=package_name,
            )
        )
