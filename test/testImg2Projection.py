import unittest
import numpy as np
from aics.image.processing.img2projection import im2projection


class Img2ProjectionTestGroup(unittest.TestCase):

    def test_arrayInput(self):
        self.assertEqual(im2projection(np.empty((1, 3, 4, 5))).shape, (3, 4, 5), "4d array input")
        self.assertEqual(im2projection(np.empty((10, 3, 4, 5))).shape, (3, 4, 5), "10 channel input")
        with self.assertRaises(ValueError):
            im2projection(np.empty((1, 1, 3, 4, 5)))
        self.assertEqual(im2projection([np.empty((3, 4, 5))] * 2).shape, (3, 4, 5), "List of 3d arrays")
        self.assertEqual(im2projection([np.empty((4, 5))] * 2).shape, (3, 4, 5), "List of 2d arrays")
        with self.assertRaises(ValueError):
            im2projection([np.array([1, 2, 3])] * 2)
        with self.assertRaises(ValueError):
            im2projection([[[[[1]]]]])

    def test_projectionMethods(self):
        test_cube = np.empty((1, 5, 5, 5))
        self.assertEqual(im2projection(test_cube, proj_method='max').shape, (3, 5, 5), "Max projection")
        with self.assertRaises(ValueError):
            im2projection(test_cube, proj_method="not-real")

    def test_colorMethods(self):
        test_cube = np.empty((1, 5, 5, 5))
        self.assertIsNotNone(im2projection(test_cube, colors='jet'), 'Color string')
        with self.assertRaises(ValueError):
            im2projection(test_cube, colors='fake_func')
        self.assertTrue((im2projection(np.ones((1, 5, 5, 5)), colors=[[255, 255, 255]])[0] == 1).all(), 'Scaling color array')
        self.assertTrue((im2projection(test_cube, colors=[[0, 1, 1]])[0] == 0).all(), 'Color cancelling with array')

    def test_colorAdjust(self):
        self.assertTrue((im2projection(np.random.random((1, 5, 5, 5)), global_adjust=True)[0] > 254).any(), 'Global color adjust')

    def test_projectAll(self):
        test_cube = np.empty((1, 5, 5, 5))
        self.assertEqual(im2projection(test_cube, proj_all=True).shape, (3, 10, 10), "Project All")

    def test_channelCombine(self):
        n = 6
        base_list = [1] + [0]*(n-1)
        # all permutations
        test_channels = [np.array([base_list[i:] + base_list[0:i]]) for i in range(n)]
        self.assertTrue((im2projection(test_channels) == 1).all())