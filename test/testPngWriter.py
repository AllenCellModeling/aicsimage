#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest

from aicsimagetools import cziReader
from aicsimagetools import pngReader
from aicsimagetools import pngWriter
from test.transformation import *


class PngWriterTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.writer = pngWriter.PngWriter(os.path.join(cls.dir_path, 'img', 'pngwriter_test_output.png'))
        with cziReader.CziReader(os.path.join(cls.dir_path, 'img', 'T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi')) as reader:
            with pngReader.PngReader(os.path.join(cls.dir_path, 'img', 'czi_output_comparison.png')) as comparisonReader:
                cls.comparison_image = comparisonReader.load()
                cls.image = np.ndarray([reader.size_z(), reader.size_c(), reader.size_y(),
                                        reader.size_x()], dtype=reader.dtype())
            for i in range(reader.size_z()):
                for j in range(reader.size_c()):
                    cls.image[i, j, :, :] = reader.load_slice(z=i, c=j)

        reader.close()

    """
    Test saves an image and compares it with a previously saved image.
    This test should assure that the png save() method works as it always has
    """
    def test_pngSaveComparison(self):
        self.writer.save(transform(self.image))
        reader = pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png'))
        output_image = reader.load()
        self.assertTrue(np.array_equal(self.comparison_image, output_image))
        reader.close()

    """
    Test saves an image with various z, c, and t.
    This should not change the behavior of save(), so the output should still be identical to the comparison_image
    """
    def test_pngSaveImageComparison(self):
        self.writer.save_image(transform(self.image), z=1, c=2, t=3)
        reader = pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png'))
        output_image = reader.load()
        self.assertTrue(np.array_equal(self.comparison_image, output_image))
        reader.close()
