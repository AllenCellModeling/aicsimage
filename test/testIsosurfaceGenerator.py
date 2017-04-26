import unittest
import numpy as np
import math as m

from aicsimage.processing import isosurfaceGenerator
from aicsimage.processing.aicsImage import AICSImage


class IsosurfaceGeneratorTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        # this method has to be included in a testgroup in order for it be run
        self.assertTrue(True)

    @staticmethod
    def testSphere(radius=11):
        bounding_cube = np.zeros((radius * 2 + 3, radius * 2 + 3, radius * 2 + 3)).astype(np.float32)
        center = bounding_cube.shape[0] // 2
        for x in range(bounding_cube.shape[0]):
            for y in range(bounding_cube.shape[1]):
                for z in range(bounding_cube.shape[2]):
                    x_dist = (x-center) ** 2
                    y_dist = (y-center) ** 2
                    z_dist = (z-center) ** 2
                    distance_from_center = m.sqrt(x_dist + y_dist + z_dist)
                    if distance_from_center <= radius:
                        bounding_cube[x, y, z] = 1
        sphere = AICSImage(bounding_cube, dims="XYZ")
        mesh = isosurfaceGenerator.generate_mesh(sphere, isovalue=.99)
        mesh.save_as_obj("./img/test_sphere.obj")
        mesh.display()

    @staticmethod
    def generate_cell_image():
        cell_image = AICSImage("/home/zacharyc/Development/aicsimage/test/img/img40_1.ome.tif")
        mesh = isosurfaceGenerator.generate_mesh(cell_image, channel=4)
        mesh.save_as_obj("./test_file.obj")
