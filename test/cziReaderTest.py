#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import cziReader
import numpy as np
import os
import unittest


class SetUpTest(unittest.TestCase):
    def setUp(self):
        self.reader = cziReader.CziReader(os.path.join('img', 'T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi'))
        self.load = self.reader.load()
        self.load_image = np.ndarray([self.reader.size_t(), self.reader.size_z(), self.reader.size_c(), self.reader.size_y(),
                                      self.reader.size_x()], dtype=self.reader.dtype())
        for i in range(self.reader.size_t()):
            for j in range(self.reader.size_z()):
                for k in range(self.reader.size_c()):
                    self.load_image[i, j, k, :, :] = self.reader.load_image(t=i, z=j, c=k)


class CziLoadDimensionTestCase(SetUpTest):
    """
    Test to check the dimensionality of the array loaded by CziReader
    This should be 4 dimensional, ZCYX, or 5 dimensional, TZCYX.
    """
    def runTest(self):
        self.assertTrue(len(self.load.shape) == 4 or len(self.load.shape) == 5)


class CziLoadImageDimensionsTestCase(SetUpTest):
    """
    Test to check the dimensionality of the array loaded by CziReader
    This should be 5 dimensional, TZCYX
    """
    def runTest(self):
        self.assertEqual(len(self.load_image.shape), 5)


class CziLoadComparisonLoadImageTestCase(SetUpTest):
    """
    Test to check if load() and load_image() (for all slices) load the same image
    """
    def runTest(self):
        self.assertTrue(np.array_equal(self.load, self.load_image))
