#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

import math as m
import os
import unittest

import numpy as np

from aics.image.io import tifReader


class TifReaderTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.reader0 = tifReader.TifReader(os.path.join(cls.dir_path, 'img', 'img40_1_dna.tif'))

    """
    Test to check the dimensionality of the array loaded by TifReader
    This should be 2 dimensional, YX
    """
    def test_tifLoadImageDimension(self):
        z_index = int(m.floor(self.reader0.size_z() / 2))
        self.assertEqual(len(self.reader0.load_slice(z=z_index).shape), 2)

    """
    Test to check the dimensionality of the array loaded by TifReader
    This should be 3 dimensional, CYX where C = rgb channels
    """
    def test_tifLoadDimension(self):
        self.assertEqual(len(self.reader0.load().shape), 3)

    """
    Test to check that loading the image through load() and load_image() doesn't
    change the output or dimensionality
    """
    def test_tifLoadComparisonTest(self):
        loaded_image_slices = np.ndarray([self.reader0.size_z(), self.reader0.size_y(),
                                          self.reader0.size_x()], dtype=self.reader0.dtype())
        for i in range(self.reader0.size_z()):
            loaded_image_slices[i, :, :] = self.reader0.load_slice(z=i)
        loaded_image = self.reader0.load()

        self.assertTrue(np.array_equal(loaded_image, loaded_image_slices))
