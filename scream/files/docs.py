from .util import File

TEMPLATE = """\
# Documentation Index

{package_links}
"""

PACKAGE_LINK_TMPL = "- [{package_name}]({package_dir}/README.md)\n"


class Docs(File):
    def __init__(self, packages=None):
        package_links = ''
        if packages:
            for package in packages:
                package_link = PACKAGE_LINK_TMPL.format(package_name=package.package_name.replace("_", "."),
                                                        package_dir=package.package_dir)
                package_links += package_link

        super(Docs, self).__init__(
            'docs.md',
            TEMPLATE.format(package_links=package_links)
        )
