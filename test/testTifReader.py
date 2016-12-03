#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import tifReader
import os
import numpy as np
import unittest


class SetUpTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.reader0 = tifReader.TifReader(os.path.join(cls.dir_path, 'img', 'img40_1_dna.tif'))
        reader1 = tifReader.TifReader(os.path.join(cls.dir_path, 'img', 'img40_1_memb.tif'))
        reader2 = tifReader.TifReader(os.path.join(cls.dir_path, 'img', 'img40_1_struct.tif'))
        reader3 = tifReader.TifReader(os.path.join(cls.dir_path, 'img', 'img40_1_seg_cell.tif'))
        reader4 = tifReader.TifReader(os.path.join(cls.dir_path, 'img', 'img40_1_seg_nuc.tif'))
        cls.load_image = np.ndarray([cls.reader0.size_z(), 5, cls.reader0.size_y(), cls.reader0.size_x()],
                                    dtype=cls.reader0.dtype())

        for i in range(cls.reader0.size_z()):
            cls.load_image[i, 0, :, :] = cls.reader0.load_slice(z=i)
            cls.load_image[i, 1, :, :] = reader1.load_slice(z=i)
            cls.load_image[i, 2, :, :] = reader2.load_slice(z=i)
            cls.load_image[i, 3, :, :] = reader3.load_slice(z=i)
            cls.load_image[i, 4, :, :] = reader4.load_slice(z=i)

        reader1.close()
        reader2.close()
        reader3.close()
        reader4.close()

    """
    Test to check the dimensionality of the array loaded by TifReader
    This should be 4 dimensional, ZCYX
    """
    def test_tifLoadImageDimension(self):
        self.assertEqual(len(self.load_image.shape), 4)

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
