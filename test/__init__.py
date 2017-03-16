import unittest
from test import testImg2Projection


def test_suite():
    return TotalTestGroup()


class TotalTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromModule(testImg2Projection))
        exitcode = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
        print('\n')
        self.assertTrue(exitcode)

    def tearDown(self):
        pass
