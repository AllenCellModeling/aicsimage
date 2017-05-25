# Author: Evan Wiederspan <evanw@alleninstitute.org>
import unittest
import numpy as np
from itertools import permutations
from aicsimage.processing.alignMajor import align_major, get_align_angles, get_major_minor_axis, angle_between


class AlignMajorTestGroup(unittest.TestCase):

    def setUp(self):
        # binary CZYX image with major along x, minor along z
        self.testCube = np.zeros((3, 10, 10, 10))
        self.testCube[:, 5, 5, :] = 1
        self.testCube[:, 5, 0:5, 5] = 1
        self.testCube[:, 6, 5, 5] = 1

    def getRandAxes(self):
        """
        Helper function to get random arrangement of 'xyz'
        """
        return "".join(np.random.permutation(['x', 'y', 'z']).tolist())

    def test_angleBetween(self):
        self.assertEqual(angle_between(np.array([0, 1]), np.array([0, 1])), 0, "0 degree check")
        self.assertEqual(angle_between(np.array([0, 1]), np.array([1, 0])), 90, "90 degree check")
        with self.assertRaises(ValueError, msg="Must take 1d numpy arrays as input"):
            angle_between(np.ones((2, 2)), np.ones((2, 2)))

    def test_getMajorMinorAxis(self):
        # binary CZYX image with major along x axis
        test = np.zeros((3, 10, 10, 10))
        test[:, 5, 5, :] = 1
        # major axis should be parallel to x axis
        major, minor = get_major_minor_axis(test)
        self.assertTrue(angle_between(major, np.array([1, 0, 0])) < 1, msg="Major Axis Pre-rotation")

    def test_alignMajorInputs(self):
        with self.assertRaises(ValueError, msg="img must be 4d numpy array"):
            align_major([[1]], "xyz")
        with self.assertRaises(ValueError, msg="axis must be arrangement of 'xyz'"):
            align_major(self.testCube, "aaa")

    def test_alignMajorAlignment(self):
        a_map = {'x': 0, 'y': 1, 'z': 2}
        # try every alignment possibility
        for axes in list("".join(p) for p in permutations("xyz")):
            angles = get_align_angles(self.testCube, axes)
            res = align_major(self.testCube, angles)
            major, minor = get_major_minor_axis(res)
            self.assertTrue(np.argmax(np.abs(major)) == a_map[axes[0]], "Major aligned correctly rotating to " + axes)
            self.assertTrue(np.argmax(np.abs(minor)) == a_map[axes[-1]], "Minor aligned correctly rotating to " + axes)

    def test_alignMajorReshape(self):
        axes = self.getRandAxes()
        angles = get_align_angles(self.testCube, axes)
        res = align_major(self.testCube, angles, False)
        self.assertEqual(self.testCube.shape, res.shape, "Shape stays constant when not reshaping with axes " + axes)

    def test_alignMajorMultiple(self):
        axes = self.getRandAxes()
        angles = get_align_angles(self.testCube, axes)
        res = align_major([self.testCube, self.testCube], angles)
        self.assertTrue(len(res) == 2, "Output same number of images as passed in")
        self.assertTrue(np.array_equal(res[0], res[1]), "Multiple images rotated by same amount")
