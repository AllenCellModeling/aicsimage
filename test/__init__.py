import unittest
import testCziReader
import testOmeTifReader
import testOmeTifWriter
import testPngReader
import testPngWriter
import testTifReader
import aicsimagetools

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
        aicsimagetools.init()

    def runTest(self):
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromModule(testCziReader))
        suite.addTest(loader.loadTestsFromModule(testOmeTifReader))
        suite.addTest(loader.loadTestsFromModule(testOmeTifWriter))
        suite.addTest(loader.loadTestsFromModule(testPngReader))
        suite.addTest(loader.loadTestsFromModule(testPngWriter))
        suite.addTest(loader.loadTestsFromModule(testTifReader))
        exitcode = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
        print('\n')
        self.assertTrue(exitcode)

    def tearDown(self):
        aicsimagetools.close()
