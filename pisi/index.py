
from package import Package
from xmlfile import XmlFile
import metadata
from ui import ui
import util
from config import config

class Index(XmlFile):

    def __init__(self):
        XmlFile.__init__(self,"PISI")
        self.sources = []
        self.packages = []

    def read(self, filename):
        """Read PSPEC file"""
        
        self.readxml(filename)

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        self.packages = [PackageInfo(p) for p in packageElts]
        
        self.unlink()
    

    def write(self, filename):
        """Write index file"""
        self.newDOM()
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)
        self.unlink()
        
    def index(self, repo_dir):

        import os
        from os.path import join, getsize
        for root, dirs, files in os.walk(repo_dir):
            for fn in files:
                if fn.endswith('.pisi'):
                    ui.info('Adding ' + fn + ' to package index\n')
                    self.add_package(join(root, fn))

    def add_package(self, path):
        package = Package(path, 'r')
        # extract control files
        util.clean_dir(config.install_dir())
        package.extract_PISI_files(config.install_dir())

        md = metadata.MetaData()
        md.read(config.install_dir() + '/metadata.xml')
        # check package semantics
        if md.verify():
            self.packages.append(md.package)
        else:
            ui.error('Package ' + fn + ' metadata corrupt\n')
