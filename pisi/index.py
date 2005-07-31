# -*- coding: utf-8 -*-
# PISI source/package index
# Author:  Eray Ozkural <eray@uludag.org.tr>

import os

from package import Package
from xmlfile import XmlFile
import metadata
import packagedb
from ui import ui
import util
from config import config
from constants import const
from purl import PUrl

class Index(XmlFile):

    def __init__(self):
        XmlFile.__init__(self,"PISI")
        self.sources = []
        self.packages = []

    def read(self, filename, repo = None):
        """Read PSPEC file"""

        self.filepath = filename
        url = PUrl(filename)
        if url.isRemoteFile():
            from fetcher import fetchUrl

            dest = os.path.join(config.index_dir(), repo)
            if not os.path.exists(dest):
                os.makedirs(dest)
            fetchUrl(url, dest, ui.Progress)

            self.filepath = os.path.join(dest, url.filename())

        self.readxml(self.filepath)

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        self.packages = [metadata.PackageInfo(p) for p in packageElts]
        
        self.unlink()
    
    def write(self, filename):
        """Write index file"""
        self.newDOM()
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)
        self.unlink()
        
    def index(self, repo_uri):
        self.repo_dir = repo_uri
        for root, dirs, files in os.walk(repo_uri):
            for fn in files:
                if fn.endswith(const.package_prefix):
                    ui.info('Adding ' + fn + ' to package index\n')
                    self.add_package(os.path.join(root, fn), repo_uri)

    def update_db(self, repo):
        pkgdb = packagedb.get_db(repo)
        pkgdb.clear()
        for pkg in self.packages:
            pkgdb.add_package(pkg)

    def add_package(self, path, repo_uri):
        package = Package(path, 'r')
        # extract control files
        util.clean_dir(config.install_dir())
        package.extract_PISI_files(config.install_dir())

        md = metadata.MetaData()
        md.read(os.path.join(config.install_dir(), const.metadata_xml))
        # TODO: in the future we'll do all of this with purl/pfile/&helpers
        # After that, we'll remove the ugly repo_uri parameter from this
        # function.
        md.package.packageURI = util.removepathprefix(repo_uri, path)
        # check package semantics
        if md.verify():
            self.packages.append(md.package)
        else:
            ui.error('Package ' + md.package.name + ': metadata corrupt\n')
