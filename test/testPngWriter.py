#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest

from aicsimagetools import pngReader
from aicsimagetools import pngWriter
from test.transformation import *


class PngWriterTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.writer = pngWriter.PngWriter(os.path.join(cls.dir_path, 'img', 'pngwriter_test_output.png'))
        # unfortunately, the rounding is necessary due to scipy.fromimage() only returning integer values for pixels
        cls.image = np.round(transform(np.random.rand(40, 3, 128, 256)))

    """
    Test saves an image and compares it with a previously saved image.
    This test should assure that the png save() method does not transpose any dimensions as it saves
    """
    def test_pngSaveComparison(self):
        self.writer.save(self.image)
        reader = pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png'))
        output_image = reader.load()
        self.assertTrue(np.array_equal(self.image, output_image))
        reader.close()

    """
    Test saves an image with various z, c, and t.
    The extra parameters should not change the output from save()'s output
    """
    def test_pngSaveImageComparison(self):
        self.writer.save_slice(self.image, z=1, c=2, t=3)
        reader = pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png'))
        output_image = reader.load()
        self.assertTrue(np.array_equal(self.image, output_image))
        reader.close()


