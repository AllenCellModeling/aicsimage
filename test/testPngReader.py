#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest

from aics.image.io import pngReader


class PngReaderTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with pngReader.PngReader(os.path.join(dir_path, 'img', 'img40_1.png')) as reader:
            cls.input = reader.load()

    """
    Test to assure that the png is always read in as a 3 dimensional array
    Will return CYX
    """
    def test_shapeOutput(self):
        self.assertEqual(len(self.input.shape), 3)
        self.assertEqual(self.input.shape[0], 3)
