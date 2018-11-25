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
