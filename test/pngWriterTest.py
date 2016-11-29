#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

from aicsimagetools import pngWriter
from aicsimagetools import cziReader
from aicsimagetools import pngReader
from transformation import *
import unittest
import os
import numpy as np


class SetUpTestCase(unittest.TestCase):
    def setUp(self):
        self.writer = pngWriter.PngWriter(os.path.join('img', 'pngwriter_test_output.png'))
        self.reader = cziReader.CziReader(os.path.join('img', 'T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi'))
        self.comparisonreader = pngReader.PngReader(os.path.join('img', 'czi_output_comparison.png'))
        self.image = np.ndarray([self.reader.size_z(), self.reader.size_c(), self.reader.size_y(),
                                 self.reader.size_x()], dtype=self.reader.dtype())
        for i in range(self.reader.size_z()):
            for j in range(self.reader.size_c()):
                self.image[i, j, :, :] = self.reader.load_image(z=i, c=j)


class PngSaveComparisonTestCase(SetUpTestCase):
    """
    Test saves an image and compares it with a previously saved image.
    This test should assure that the png save() method works as it always has
    """
    def runTest(self):
        self.writer.save(transform(self.image))
        comparison_image = self.comparisonreader.load()
        output_image = pngReader.PngReader(os.path.join('img', 'pngwriter_test_output.png')).load()
        self.assertTrue(np.array_equal(comparison_image, output_image))


class PngSaveImageComparisonTestCase(SetUpTestCase):
    """
    Test saves an image with various z, c, and t.
    This should not change the behavior of save(), so the output should still be identical to the comparison_image
    """
    def runTest(self):
        self.writer.save_image(transform(self.image), z=1, c=2, t=3)
        comparison_image = self.comparisonreader.load()
        output_image = pngReader.PngReader(os.path.join('img', 'pngwriter_test_output.png')).load()
        self.assertTrue(np.array_equal(comparison_image, output_image))
