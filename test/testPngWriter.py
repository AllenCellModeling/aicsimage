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
        # unfortunately, the rounding is necessary - scipy.fromimage() only returns integer values for pixels
        cls.image = np.round(transform(np.random.rand(40, 3, 128, 256)))

    """
    Test saves an image and compares it with a previously saved image.
    This test should assure that the png save() method does not transpose any dimensions as it saves
    """
    def test_pngSaveComparison(self):
        self.writer.save(self.image, overwrite_file=True)
        reader = pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png'))
        output_image = reader.load()
        self.assertTrue(np.array_equal(self.image, output_image))
        reader.close()

    """
    Test saves an image with various z, c, and t.
    The extra parameters should not change the output from save()'s output
    """
    def test_pngSaveImageComparison(self):
        self.writer.save_slice(self.image, z=1, c=2, t=3, overwrite_file=True)
        reader = pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png'))
        output_image = reader.load()
        self.assertTrue(np.array_equal(self.image, output_image))
        reader.close()

    def test_twoDimensionalImages(self):
        image = np.ndarray([2, 2], dtype=np.uint8)
        image[0, 0] = 255
        image[0, 1] = 0
        image[1, 0] = 0
        image[1, 1] = 255
        self.writer.save(image, overwrite_file=True)
        with pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png')) as reader:
            loaded_image = reader.load()
            self.assertTrue(np.array_equal(image, loaded_image))

    def test_threeDimensionalImages(self):
        image = np.zeros([1, 2, 2], dtype=np.uint8)
        image[0, 0, 0] = 255
        image[0, 0, 1] = 0
        image[0, 1, 0] = 0
        image[0, 1, 1] = 255
        self.writer.save(image, overwrite_file=True)
        with pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png')) as reader:
            # we know that the channels will be repeated, so only check the bottommost channel
            loaded_image = reader.load()[0, :, :]
            sliced_image = image[0, :, :]
            self.assertTrue(np.array_equal(loaded_image, sliced_image))

    def test_fourDimensionalImages(self):
        image = np.random.rand(1, 2, 3, 4)
        # the pngwriter cannot handle 4d images, and should thus throw an error
        with self.assertRaises(ValueError):
            self.writer.save(image, overwrite_file=True)
