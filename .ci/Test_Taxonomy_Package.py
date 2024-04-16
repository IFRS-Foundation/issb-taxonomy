import os
import sys

from arelle import ModelXbrl, ModelManager, Cntlr, Validate, FileSource
from arelle.PackageManager import parsePackage

path = r'../ifrs_sds.zip'


class TestTaxonomyPackage():

    def test_taxonomy_package(self):
        self.cntlr = Cntlr.Cntlr()
        filesource = FileSource.openFileSource(path, self.cntlr)
        if filesource.isArchive:
            if not filesource.selection:
                filenames = filesource.dir
                if filenames is not None:  # an IO or other error can return None
                    if filesource.isTaxonomyPackage:
                        filesource.loadTaxonomyPackageMappings()  # if a package, load mappings if not loaded yet
                        self.readEntryPoints(filesource)
                        for name, urls in sorted(self.taxonomyPackage["entryPoints"].items(), key=lambda i: i[0][2]):
                            self.validate_entry_point_from_package(filesource, name, urls)
                        return
        raise IOError("File is not taxonomy package")

    def readEntryPoints(self, filesource:FileSource):
        metadataFiles = filesource.taxonomyPackageMetadataFiles
        if len(metadataFiles) != 1:
            raise IOError("Taxonomy package contained more than one metadata file: {0}."
                          .format(', '.join(metadataFiles)))

        metadataFile = metadataFiles[0]
        metadata = filesource.basefile + os.sep + metadataFile
        self.metadataFilePrefix = os.sep.join(os.path.split(metadataFile)[:-1])
        if self.metadataFilePrefix:
            self.metadataFilePrefix += "/"  # zip contents have /, never \ file seps
        self.taxonomyPkgMetaInf = '{}/META-INF/'.format(
                    os.path.splitext(os.path.basename(filesource.url))[0])

        self.taxonomyPackage = parsePackage(self.cntlr, filesource, metadata,
                                            os.sep.join(os.path.split(metadata)[:-1]) + os.sep)

        if not self.taxonomyPackage["entryPoints"]:
            raise IOError("Taxonomy package contained no entry points")

    def validate_entry_point_from_package(self, filesource, name, urls):
        print('Validating '+name)
        filesource.select(urls[0][1])
        modelManager = ModelManager.initialize(self.cntlr)
        xbrl = ModelXbrl.load(modelManager, filesource)
        Validate.validate(xbrl)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        path = args[0]
    TestTaxonomyPackage().test_taxonomy_package()