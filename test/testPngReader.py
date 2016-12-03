#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

from aicsimagetools import pngReader
import os
import unittest


class PngReaderTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with pngReader.PngReader(os.path.join(dir_path, 'img', 'img40_1.png')) as reader:
            cls.array_to_check = reader.load()

    """
    Test to assure that the png is always read in as a 3 dimensional array
    Will return XYC
    """
    def test_shapeOutput(self):
        self.assertEqual(len(self.array_to_check.shape), 3)

