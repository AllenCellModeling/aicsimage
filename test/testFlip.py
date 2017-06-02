# Author: Evan Wiederspan <evanw@alleninstitute.org>

import unittest
import numpy as np
from aicsimage.processing.flip import get_flips, flip
from random import sample, randrange
from scipy.ndimage.measurements import center_of_mass


class FlipTestGroup(unittest.TestCase):

    def test_getFlipsCalc(self):
        for i in range(5):
            test = np.zeros((3, 10, 10, 10))
            test[:, 7:, 7:, 7:] = 1
            test_flips = sample(range(-3, 0), randrange(1, 4))
            for a in test_flips:
                test = np.flip(test, a)
            calc_flips = get_flips(test, "+++")
            self.assertEqual(sorted(test_flips), sorted(calc_flips), "Flip calc test: {}, {}".format(test_flips, calc_flips))

    def test_getFlipsInput(self):
        test = np.zeros((3, 10, 10, 10))
        with self.assertRaises(ValueError, msg="Sec and axes length must be equal"):
            get_flips(test, "++++")
        with self.assertRaises(ValueError, msg="Sec must contain valid characters"):
            get_flips(test, "aaa")
        with self.assertRaises(ValueError, msg="img must be a numpy array"):
            get_flips([1], "+++", axes=[0])

    def test_getFlipsAxes(self):
        test = np.zeros((3, 10, 10, 10))
        test[:, 7:, 7:, 7:] = 1
        flips = get_flips(test, "---", (-3, -2, -1))
        self.assertEqual(sorted(flips), [-3, -2, -1])
        flips = get_flips(test, "--", (-3, -2))
        self.assertEqual(sorted(flips), [-3, -2])

    def test_flips(self):
        test = np.zeros((3, 10, 10, 10))
        test[:, 7:, 7:, 7:] = 1
        test_com = center_of_mass(test)
        flips = get_flips(test, "---")
        res = flip(test, flips)
        res_com = center_of_mass(res)
        self.assertTrue(all(r < t for r, t in zip(res_com[1:], test_com[1:])), "Center of mass should move")

    def test_flipList(self):
        test = np.zeros((3, 10, 10, 10))
        test[:, 7:, 7:, 7:] = 1
        flips = get_flips(test, "---")
        res, res2 = flip([test, test], flips)
        self.assertTrue(np.array_equal(res, res2), "Multiple images flipped the same")