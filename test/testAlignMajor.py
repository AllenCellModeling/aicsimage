import unittest
import numpy as np
from aics.image.processing.alignMajor import alignMajor, getMajorMinorAxis, angleBetween


class AlignMajorTestGroup(unittest.TestCase):

    def test_angleBetween(self):
        self.assertEqual(angleBetween(np.array([0, 1]), np.array([0, 1])), 0, "0 degree check")
        self.assertEqual(angleBetween(np.array([0, 1]), np.array([1, 0])), 90, "90 degree check")
        with self.assertRaises(ValueError, msg="Must take 1d numpy arrays as input"):
            angleBetween(np.ones((2, 2)), np.ones((2, 2)))

    def test_getMajorMinorAxis(self):
        # binary CZYX image with major along x axis
        testCube = np.zeros((3, 10, 10, 10))
        testCube[:, 5, 5, :] = 1
        # major axis should be parallel to x axis
        major, minor = getMajorMinorAxis(testCube)
        self.assertTrue(angleBetween(major, np.array([1, 0, 0])) < 1, msg="Major Axis Pre-rotation")

    def test_alignMajor(self):
        # binary CZYX image with major along x, minor along z
        testCube = np.zeros((3, 10, 10, 10))
        testCube[:, 5, 5, :] = 1
        testCube[:, 5, 0:5, 5] = 1
        testCube[:, 6, 5, 5] = 1
        with self.assertRaises(ValueError, msg="img must be 4d numpy array"):
            alignMajor([[1]], "xyz")
        # self.assertIsNotNone(alignMajor(testCube, 'xyz'), "Standard test")
        with self.assertRaises(ValueError, msg="axis must be arrangement of 'xyz'"):
            alignMajor(testCube, "aaa")
        # functionality check
        res = alignMajor(testCube, "zyx")
        major, minor = getMajorMinorAxis(res)
        self.assertTrue(np.argmax(np.abs(major)) == 2, "Major aligned with Z axis after rotation")
        self.assertTrue(np.argmax(np.abs(minor)) == 0, "Minor aligned with X axis after rotation")
        # check reshaping
        self.assertEqual(testCube.shape, res.shape, "Shape stays constant when not reshaping")
        # compare output shape to input shape element-wise
        # output shape should be greater than or equal to input shape for 
        # every dimension
        res_reshaped = alignMajor(testCube, "zyx", reshape=True)
        # There are cases where reshaping could result in the same output shape
        # as the input, but this isn't one of those
        self.assertTrue(res_reshaped.shape != testCube.shape, "Shape changes with reshaping")
