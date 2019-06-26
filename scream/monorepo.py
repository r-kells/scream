import collections

from scream.files import Docs, Scream, Tox


class Monorepo(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.config = Scream(self.root_dir)

    def sync(self):
        """Used internally ensure monorepo maintains certain standards.
        """
        self.config = Scream(self.root_dir)
        Tox(self.config.packages).write(self.root_dir)
        Docs(self.config.packages).write(self.root_dir)

    def validate_mono_repo(self):
        all_pypi_packages = self.get_all_pypi_packages()

        warn_unpinned = self.warn_unpinned_packages(all_pypi_packages)
        warn_dependency_conflict = self.warn_dependency_conflict(all_pypi_packages)

        for package in self.config.packages:
            self.intersect_warning(package.package_name, "has unpinned dependencies",
                                   warn_unpinned, package.other_dependencies)
            self.intersect_warning(package.package_name, "more than 1 package has a different version for",
                                   warn_dependency_conflict, package.other_dependencies)

    def warn_unpinned_packages(self, pypi_packages):
        to_report_packages = []
        for p in pypi_packages:
            if "==" not in p:
                to_report_packages.append(p)
        return to_report_packages

    def warn_dependency_conflict(self, pypi_packages):
        to_report_packages = []

        counts = version_counter(pypi_packages)
        for p in pypi_packages:
            if len(counts[(p.split("==")[0])]) > 1:
                to_report_packages.append(p)
        return to_report_packages

    def get_all_pypi_packages(self):
        p = []
        for package in self.config.packages:
            p.extend(package.other_dependencies)
        return p

    @staticmethod
    def intersect_warning(name, description, list1, list2):
        intersect = set(list1).intersection(set(list2))
        if intersect:
            print("Warning: Package {name} {description}: {intersect}.".format(
                name=name,
                description=description,
                intersect=', '.join(intersect)
            ))


def version_counter(pypi_packages):
    results = collections.defaultdict(set)
    for p in pypi_packages:
        try:
            name, version = p.split("==")
        except Exception:
            name = p.split("==")[0]
            version = 'LATEST'
        results[name].update([version])
    return results
