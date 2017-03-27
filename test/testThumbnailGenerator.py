#!/usr/bin/env python

# author: Zach Crabtree zacharyc@alleninstitute.org

import unittest
import numpy as np
from aics.image.processing.thumbnailGenerator import ThumbnailGenerator


class ThumbnailGeneratorTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        # this method has to be included in a testgroup in order for it be run
        self.assertTrue(True)

    """Constructor tests"""

    def test_ColorsConstructor(self):
        # arrange
        valid_color_palette = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

        # act, assert
        generator = ThumbnailGenerator(colors=valid_color_palette)
        self.assertIsNotNone(generator)

    def test_InvalidColorsConstructor(self):
        # arrange
        invalid_color_palette = [['a', 'b', 'c', 'd']]

        # act, assert
        with self.assertRaises(Exception):
            generator = ThumbnailGenerator(colors=invalid_color_palette)

    def test_ChannelIndicesConstructor(self):
        # arrange
        valid_channel_indices = [0, 1, 2]
        # act
        generator = ThumbnailGenerator(channel_indices=valid_channel_indices)
        # assert
        self.assertIsNotNone(generator)

    """make_thumbnail tests"""

    def test_MakeValidThumbnail(self):
        # arrange
        valid_image = np.random.rand(10, 7, 16, 16)
        generator = ThumbnailGenerator(size=128)

        # act
        valid_thumbnail = generator.make_thumbnail(valid_image)

        # assert
        self.assertEqual(valid_thumbnail.shape, (4, 128, 128))

    def test_MakeOddlySizedThumbnail(self):
        # arrange
        valid_image = np.random.rand(1, 7, 2, 2)
        generator = ThumbnailGenerator(size=128)

        # act
        valid_thumbnail = generator.make_thumbnail(valid_image)

        # assert
        self.assertEqual(valid_thumbnail.shape, (4, 128, 128))

    def test_MakeInvalidThumbnail(self):
        # arrange
        invalid_image = np.random.rand(1, 5, 128, 128)  # < 6 channels should be an invalid image
        generator = ThumbnailGenerator(size=128)

        # act, assert
        with self.assertRaises(Exception):
            generator.make_thumbnail(invalid_image)
