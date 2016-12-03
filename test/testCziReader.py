#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import cziReader
import numpy as np
import os
import unittest


class CziReaderTestGroup(unittest.TestCase):

    @classmethod
    def setUp(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reader = cziReader.CziReader(os.path.join(dir_path, 'img', 'T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi'))
        # with cziReader.CziReader(os.path.join(dir_path, 'img', 'T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi')) as reader:
        cls.load = reader.load()
        cls.load_image = np.ndarray([reader.size_t(), reader.size_z(), reader.size_c(),
                                      reader.size_y(), reader.size_x()], dtype=reader.dtype())
        for i in range(reader.size_t()):
            for j in range(reader.size_z()):
                for k in range(reader.size_c()):
                    cls.load_image[i, j, k, :, :] = reader.load_slice(t=i, z=j, c=k)

        reader.close()

    """
    Test to check the dimensionality of the array loaded by CziReader
    This should be 4 dimensional, ZCYX, or 5 dimensional, TZCYX.
    """
    def test_loadDimension(self):
        self.assertTrue(len(self.load.shape) == 4 or len(self.load.shape) == 5, msg="Shape is not 4 or 5")

    """
    Test to check the dimensionality of the array loaded by CziReader
    This should be 5 dimensional, TZCYX
    """
    def test_loadImageDimensions(self):
        self.assertEqual(len(self.load_image.shape), 5)

    """
    Test to check if load() and load_image() (for all slices) load the same image
    """
    def test_compareLoadMethodResults(self):
        self.assertTrue(np.array_equal(self.load, self.load_image))
