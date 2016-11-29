#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import tifReader
import os
import numpy as np
import unittest


class SetUpTestCase(unittest.TestCase):
    def setUp(self):
        self.reader0 = tifReader.TifReader(os.path.join('img', 'img40_1_dna.tif'))
        self.reader1 = tifReader.TifReader(os.path.join('img', 'img40_1_memb.tif'))
        self.reader2 = tifReader.TifReader(os.path.join('img', 'img40_1_struct.tif'))
        self.reader3 = tifReader.TifReader(os.path.join('img', 'img40_1_seg_cell.tif'))
        self.reader4 = tifReader.TifReader(os.path.join('img', 'img40_1_seg_nuc.tif'))
        self.load_image = np.ndarray([self.reader0.size_z(), 5, self.reader0.size_y(), self.reader0.size_x()],
                                     dtype=self.reader0.dtype())

        for i in range(self.reader0.size_z()):
            self.load_image[i, 0, :, :] = self.reader0.load_image(z=i)
            self.load_image[i, 1, :, :] = self.reader1.load_image(z=i)
            self.load_image[i, 2, :, :] = self.reader2.load_image(z=i)
            self.load_image[i, 3, :, :] = self.reader3.load_image(z=i)
            self.load_image[i, 4, :, :] = self.reader4.load_image(z=i)


class TifLoadImageDimensionTestCase(SetUpTestCase):
    """
    Test to check the dimensionality of the array loaded by TifReader
    This should be 4 dimensional, ZCYX
    """
    def runTest(self):
        self.assertEqual(len(self.load_image.shape), 4)


class TifLoadDimensionTestCase(SetUpTestCase):
    """
    Test to check the dimensionality of the array loaded by TifReader
    This should be 3 dimensional, CYX where C = rgb channels
    """
    def runTest(self):
        self.assertEqual(len(self.reader0.load().shape), 3)


class TifLoadComparisonTestCase(SetUpTestCase):
    """
    Test to check that loading the image through load() and load_image() doesn't
    change the output or dimensionality
    """
    def runTest(self):
        loaded_image_slices = np.ndarray([self.reader0.size_z(), self.reader0.size_y(),
                                          self.reader0.size_x()], dtype=self.reader0.dtype())
        for i in range(self.reader0.size_z()):
            loaded_image_slices[i, :, :] = self.reader0.load_image(z=i)
        loaded_image = self.reader0.load()

        self.assertTrue(np.array_equal(loaded_image, loaded_image_slices))
