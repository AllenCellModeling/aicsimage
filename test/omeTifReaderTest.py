#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import omeTifReader
import os
import numpy as np
import unittest


class SetUpTestCase(unittest.TestCase):
    def setUp(self):
        self.reader = omeTifReader.OmeTifReader(os.path.join('img', 'img40_1.ome.tif'))
        self.load = self.reader.load()
        self.load_image = np.ndarray([self.reader.size_z(), self.reader.size_c(), self.reader.size_y(),
                                      self.reader.size_x()], dtype=self.reader.dtype())
        for i in range(self.reader.size_z()):
            for j in range(self.reader.size_c()):
                self.load_image[i, j, :, :] = self.reader.load_image(z=i, c=j)


class OmeTifLoadDimensionTestCase(SetUpTestCase):
    """
    Test to check the dimensionality of the array loaded by OmeTifReader
    This should be 4 dimensional, ZCYX
    (Is there a way to test that the dimensions are in the right order?)
    """
    def runTest(self):
        self.assertEqual(len(self.load.shape), 4)


class OmeTifLoadImageDimensionTestCase(SetUpTestCase):
    """
    Test to check the dimensionality of the array loaded by OmeTifReader
    This should be 4 dimensional, ZCYX
    """
    def runTest(self):
        self.assertEqual(len(self.load_image.shape), 4)


class OmeTifLoadCompareLoadImageTestCase(SetUpTestCase):
    """
    Test to check if load() and load_image() (for all slices) load the same image
    """
    def runTest(self):
        self.assertTrue(np.array_equal(self.load, self.load_image))
