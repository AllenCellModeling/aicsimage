import unittest

import numpy as np

from aicsimage.processing.alignMajor import align_major, get_major_minor_axis, angle_between


class AlignMajorTestGroup(unittest.TestCase):

    def test_angleBetween(self):
        self.assertEqual(angle_between(np.array([0, 1]), np.array([0, 1])), 0, "0 degree check")
        self.assertEqual(angle_between(np.array([0, 1]), np.array([1, 0])), 90, "90 degree check")
        with self.assertRaises(ValueError, msg="Must take 1d numpy arrays as input"):
            angle_between(np.ones((2, 2)), np.ones((2, 2)))

    def test_getMajorMinorAxis(self):
        # binary CZYX image with major along x axis
        testCube = np.zeros((3, 10, 10, 10))
        testCube[:, 5, 5, :] = 1
        # major axis should be parallel to x axis
        major, minor = get_major_minor_axis(testCube)
        self.assertTrue(angle_between(major, np.array([1, 0, 0])) < 1, msg="Major Axis Pre-rotation")

    def test_alignMajor(self):
        # binary CZYX image with major along x, minor along z
        testCube = np.zeros((3, 10, 10, 10))
        testCube[:, 5, 5, :] = 1
        testCube[:, 5, 0:5, 5] = 1
        testCube[:, 6, 5, 5] = 1
        with self.assertRaises(ValueError, msg="img must be 4d numpy array"):
            align_major([[1]], "xyz")
        # self.assertIsNotNone(alignMajor(testCube, 'xyz'), "Standard test")
        with self.assertRaises(ValueError, msg="axis must be arrangement of 'xyz'"):
            align_major(testCube, "aaa")
        # functionality check
        res = align_major(testCube, "zyx")
        major, minor = get_major_minor_axis(res)
        self.assertTrue(np.argmax(np.abs(major)) == 2, "Major aligned with Z axis after rotation")
        self.assertTrue(np.argmax(np.abs(minor)) == 0, "Minor aligned with X axis after rotation")
        # check reshaping
        self.assertEqual(testCube.shape, res.shape, "Shape stays constant when not reshaping")
