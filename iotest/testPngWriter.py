#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest

from aics.image.io import pngReader

from io import pngWriter
from iotest.transformation import *


class PngWriterTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.writer = pngWriter.PngWriter(os.path.join(cls.dir_path, 'img', 'pngwriter_test_output.png'),
                                         overwrite_file=True)
        # unfortunately, the rounding is necessary - scipy.fromimage() only returns integer values for pixels
        cls.image = np.round(transform(np.random.rand(40, 3, 128, 256)))

    """
    Test saves an image and compares it with a previously saved image.
    This iotest should assure that the png save() method does not transpose any dimensions as it saves
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

    """
    Test saves an image with a single xy plane
    This iotest assures that the pixels are written to the correct orientation
    """
    def test_twoDimensionalImages(self):
        image = np.ndarray([2, 2], dtype=np.uint8)
        image[0, 0] = 255
        image[0, 1] = 0
        image[1, 0] = 0
        image[1, 1] = 255
        self.writer.save(image)
        with pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png')) as reader:
            loaded_image = reader.load()
            self.assertTrue(np.array_equal(image, loaded_image))

    """
    Test saves an image with a single xy plane, but gives one channel
    This iotest assures that the channels are repeated when written with less than 3 channels
    """
    def test_threeDimensionalImages(self):
        image = np.zeros([1, 2, 2], dtype=np.uint8)
        image[0, 0, 0] = 255
        image[0, 0, 1] = 0
        image[0, 1, 0] = 0
        image[0, 1, 1] = 255
        self.writer.save(image)
        with pngReader.PngReader(os.path.join(self.dir_path, 'img', 'pngwriter_test_output.png')) as reader:
            all_channels = reader.load()
            channel_r = all_channels[0, :, :]
            channel_g = all_channels[1, :, :]
            channel_b = all_channels[2, :, :]
            self.assertTrue(np.array_equal(channel_r, channel_g) and np.array_equal(channel_g, channel_b) and np.array_equal(channel_r, image[0, :, :]))

    """
    Test attempts to save an image with zcyx dims
    This should fail because the pngwriter does not accept images with more than 3 dims
    """
    def test_fourDimensionalImages(self):
        image = np.random.rand(1, 2, 3, 4)
        # the pngwriter cannot handle 4d images, and should thus throw an error
        with self.assertRaises(Exception):
            self.writer.save(image)
