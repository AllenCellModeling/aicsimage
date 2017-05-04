import unittest

from aicsimage.io import init, close
from . import testAICSImage
from . import testAlignMajor
from . import testBackgroundCrop
from . import testBackgroundSub
from . import testCziReader
from . import testImgToProjection
from . import testOmeTifReader
from . import testOmeTifWriter
from . import testPngReader
from . import testPngWriter
from . import testThumbnailGenerator
from . import testTifReader


"""
To test all modules with the command line, use:
    python setup.py test

To test individual modules with the command line, use:
    python -m unittest discover --pattern=test_module.py

It is a possibility to test a few modules at a time with a regex pattern:
    python -m unittest discover --pattern=*Reader.py
However, this can cause issues with the **bioformats** implementation because the JVM
will crash after one or more instantiations
"""


def test_suite():
    return TotalTestGroup()


class TotalTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)
        init()

    def runTest(self):
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromModule(testThumbnailGenerator))
        suite.addTest(loader.loadTestsFromModule(testImgToProjection))
        suite.addTest(loader.loadTestsFromModule(testCziReader))
        suite.addTest(loader.loadTestsFromModule(testOmeTifReader))
        suite.addTest(loader.loadTestsFromModule(testOmeTifWriter))
        suite.addTest(loader.loadTestsFromModule(testPngReader))
        suite.addTest(loader.loadTestsFromModule(testPngWriter))
        suite.addTest(loader.loadTestsFromModule(testAlignMajor))
        suite.addTest(loader.loadTestsFromModule(testBackgroundCrop))
        suite.addTest(loader.loadTestsFromModule(testBackgroundSub))
        suite.addTest(loader.loadTestsFromModule(testImgCenter))
        suite.addTest(loader.loadTestsFromModule(testAICSImage))
        exitcode = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
        print('\n')
        self.assertTrue(exitcode)

    def tearDown(self):
        close()
