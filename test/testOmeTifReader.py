#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import omeTifReader
import os
import numpy as np
import unittest


class OmeTifReaderTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reader = omeTifReader.OmeTifReader(os.path.join(dir_path, 'img', 'img40_1.ome.tif'))
        cls.load = reader.load()
        cls.load_image = np.ndarray([reader.size_z(), reader.size_c(), reader.size_y(), reader.size_x()],
                                    dtype=reader.dtype())
        for i in range(reader.size_z()):
            for j in range(reader.size_c()):
                cls.load_image[i, j, :, :] = reader.load_slice(z=i, c=j)

        reader.close()

    def test_omeTifLoadShapeCorrectDimensions(self):
        self.assertEqual(len(self.load.shape), 4)

    def test_omeTifLoadImageShapeCorrectDimensions(self):
        self.assertEqual(len(self.load_image.shape), 4)

    def test_omeTifLoadCompareLoadImage(self):
        self.assertTrue(np.array_equal(self.load, self.load_image))



