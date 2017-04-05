# Author: Evan Wiederspan
import unittest
from processing.resize import resize, resize_to
import numpy as np
from random import randrange


class ImgResizeTestGroup(unittest.TestCase):

    def test_resizeOutput(self):
        test_cube = np.empty((2, 2, 2))
        self.assertEqual(resize(test_cube, 2).shape, (4, 4, 4), "Basic scaling")
        # arbitrary number of dimensions
        n_dim = randrange(1, 10)
        rand_cube = np.empty(([2]*n_dim))
        self.assertEqual(resize(rand_cube, 2).shape, tuple([4] * n_dim), "Arbitrary dimension scaling")
        # also takes in list for each dimension
        self.assertEqual(resize(rand_cube, [2] * n_dim).shape, tuple([4] * n_dim), "Individual dimension scaling")
        # works for floats and zeros
        self.assertEqual(resize(test_cube, (1.5, 0.5, 0)).shape, (3, 1, 0), "Scale by floats or zero")

    def test_resizeInputs(self):
        with self.assertRaises(ValueError, msg="Must take in a numpy array"):
            resize(4, 1)
        test_cube = np.empty((3, 3, 3))
        with self.assertRaises(ValueError, msg="Resize factor cannot be negative"):
            resize(test_cube, -1)
        with self.assertRaises(ValueError, msg="Factor list cannot contain negatives"):
            resize(test_cube, (2, 2, -1))
        # only accept certain methods
        self.assertEqual(resize(test_cube, 3, method='bilinear').shape, (9, 9, 9), "Resize Bilinear")
        self.assertEqual(resize(test_cube, 3, method='cubic').shape, (9, 9, 9), "Resize Cubic")
        with self.assertRaises(ValueError, msg="Resize method must exist"):
            resize(test_cube, 2, method="not-real")

    def test_resizetoInputs(self):
        # out_size must be a iterable of same sized
        test_cube = np.empty((3, 3, 3))
        self.assertEqual(resize_to(test_cube, (9, 9, 9), method="bilinear").shape, (9, 9, 9), "Resize_to Bilinear")
        self.assertEqual(resize_to(test_cube, (9, 9, 9), method="cubic").shape, (9, 9, 9), "Resize_to Cubic")
        with self.assertRaises(ValueError, msg="out_size must be the same length as the input size"):
            resize_to(test_cube, (3, 3, 3, 3))
        with self.assertRaises(ValueError, msg="out_size cannot contain negatives"):
            resize_to(test_cube, (9, 9, -9))
        # only accept certain methods
        with self.assertRaises(ValueError, msg="Resize method must exist"):
            resize_to(test_cube, (9, 9, 9), method="not-real")

    def test_resizetoOutput(self):
        n_dim = 4
        # create ten randomized tests
        for t in range(10):
            arr_input = tuple(randrange(0, 20) for i in range(n_dim))
            arr_output = tuple(randrange(0, 20) for i in range(n_dim))
            out = resize_to(np.empty(arr_input), arr_output)
            self.assertEqual(out.shape, 
                             tuple(0 if a == 0 else b for a, b in zip(arr_input, arr_output)),
                             "Random Resize_to {} -> {}, got {}".format(arr_input, arr_output, out.shape))
