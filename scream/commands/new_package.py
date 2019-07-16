import os
from scream.files import Deploy, PackageReadme, ModuleExample, SetupCfg, SetupPy, TestExample
from scream.files.util import File

NAMESPACE_INIT = "__path__ = __import__('pkgutil').extend_path(__path__, __name__)\n"


def new_package(d, namespaces, package_name):
    """Creates a new package inside a directory `d`.
    Args:
        d (str): The new package dir.
        namespaces: (list)strings: names of the packages namspace(s).
        package_name (str): the package name.

    Example:
        scream new example_pkg
    """
    # For differences in namespace package naming requirements see...
    # https://github.com/pypa/sample-namespace-packages/tree/master/pkgutil
    full_package_name = '.'.join(namespaces) + '.' + package_name
    setup_py_package_name = full_package_name.replace('.', '_')

    # Build namespace dir structure...
    namespace_dir = ''
    namespace_path = ''

    for namespace in namespaces:
        namespace_path = os.path.join(namespace_path, namespace)
        namespace_dir = os.path.join(d, namespace_path)
        init_py = File('__init__.py', NAMESPACE_INIT)
        init_py.write(namespace_dir)

    package_dir = os.path.join(d, namespace_dir, package_name)
    File('__init__.py', '').write(package_dir)
    ModuleExample().write(package_dir)

    tests_dir = os.path.join(d, 'tests')
    File('__init__.py', '').write(tests_dir)
    TestExample(full_package_name).write(tests_dir)

    Deploy(package_name).write(d)
    PackageReadme(full_package_name).write(d)
    SetupCfg(setup_py_package_name).write(d)
    SetupPy().write(d)
