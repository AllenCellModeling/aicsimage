import unittest
import numpy as np
import math as m
import mcubes

from aicsimage.processing import isosurfaceGenerator
from aicsimage.processing.aicsImage import AICSImage


class IsosurfaceGeneratorTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        # this method has to be included in a testgroup in order for it be run
        self.assertTrue(True)

    @staticmethod
    def testSphere(radius=30):
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
        mcubes.export_mesh(mesh.verts, mesh.faces, "img/test_sphere.dae", "sphere")
        mesh.save_as_obj("img/test_sphere.obj")
        # mesh.display()

    @staticmethod
    def testCube(size=4):
        # these cubes appear to have strangely beveled edges but I think that is an artifact of the
        # linear interpolation between values of the marching cubes algorithm.
        cube = np.zeros((size, size, size))
        for x in range(cube.shape[0]):
            for y in range(cube.shape[1]):
                for z in range(cube.shape[2]):
                    if x != 0 and y != 0 and z != 0 and x != size-1 and y != size-1 and z != size-1:
                        cube[x, y, z] = 1
        cube = AICSImage(cube, dims="XYZ")
        mesh = isosurfaceGenerator.generate_mesh(cube, isovalue=.5)
        mcubes.export_mesh(mesh.verts, mesh.faces, "img/test_cube.dae", "cube")
        mesh.save_as_obj("img/test_cube.obj")

    @staticmethod
    def testCellImage():
        cell_image = AICSImage("/home/zacharyc/Development/aicsimage/test/img/img40_1.ome.tif")
        mesh = isosurfaceGenerator.generate_mesh(cell_image, channel=4)
        mcubes.export_mesh(mesh.verts, mesh.faces, "img/test_cell.dae", "cell")
        mesh.save_as_obj("img/test_file.obj")
