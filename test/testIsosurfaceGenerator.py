import unittest

from aicsimage.processing import isosurfaceGenerator
from aicsimage.processing.aicsImage import AICSImage


class IsosurfaceGeneratorTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        # this method has to be included in a testgroup in order for it be run
        self.assertTrue(True)

    def generateSphere(self):
        cell_image = AICSImage("/home/zacharyc/Development/aicsimage/test/img/img40_1.ome.tif")
        mesh = isosurfaceGenerator.generate_mesh(cell_image, channel=4, scaling=1)
        mesh.save_as_obj("./test_file.obj")