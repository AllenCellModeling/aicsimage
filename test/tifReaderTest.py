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
        self.reader_array = [self.reader0, self.reader1, self.reader2, self.reader3, self.reader4]
        self.load_image = np.ndarray([self.reader_array[0].size_z(), 5, self.reader_array[0].size_y(),
                                self.reader_array[0].size_x()], dtype=self.reader_array[0].dtype())
        for i in range(self.reader_array[0].size_z()):
            self.load_image[i, 0, :, :] = self.reader_array[0].load_image(z=i)
            self.load_image[i, 1, :, :] = self.reader_array[1].load_image(z=i)
            self.load_image[i, 2, :, :] = self.reader_array[2].load_image(z=i)
            self.load_image[i, 3, :, :] = self.reader_array[3].load_image(z=i)
            self.load_image[i, 4, :, :] = self.reader_array[4].load_image(z=i)


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
    This should be 4 dimensional, ZCYX
    (But it's not right now, the load function only returns a ZYX array)
    (Would it be worth it to just extend an empty c dimension in the method?)
    (for the sample files, it would return an array of z = 42, c = 1, y = 410, x = 286)
    """
    def runTest(self):
        self.load = self.reader0.load()
