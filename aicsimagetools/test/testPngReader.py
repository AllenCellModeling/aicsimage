#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest
from aicsimagetools import pngReader


class SetUpTestCase(unittest.TestCase):
    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.reader = pngReader.PngReader(os.path.join(dir_path, 'img', 'img40_1.png'))


class PngReaderShapeComparisonTestCase(SetUpTestCase):
    """
    Test to assure that the png is always read in as a 3 dimensional array
    Will return XYC
    """
    def runTest(self):
        array_to_check = self.reader.load()
        self.assertEqual(len(array_to_check.shape), 3)
