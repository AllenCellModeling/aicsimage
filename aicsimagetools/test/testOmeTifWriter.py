#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest
import numpy as np
from aicsimagetools import omeTifWriter
from aicsimagetools import omeTifReader


class SetUpTestCase(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.writer = omeTifWriter.OmeTifWriter(os.path.join(self.dir_path, 'img', 'ometiftest_output.ome.tif'))
        self.reader = omeTifReader.OmeTifReader(os.path.join(self.dir_path, 'img', 'img40_1.ome.tif'))


class OmeTifWriterShapeComparisonTestCase(SetUpTestCase):
    """
    Test to check that OmeTifWriter saves arrays that are reflexive with OmeTifReader
    """
    def runTest(self):
        comparison_array = self.reader.load()
        self.writer.save(comparison_array)
        output_reader = omeTifReader.OmeTifReader(os.path.join(self.dir_path, 'img', 'ometiftest_output.ome.tif'))
        writer_output_array = output_reader.load()
        self.assertEqual(comparison_array.shape, writer_output_array.shape)


class OmeTifWriterDimensionTestCase(SetUpTestCase):
    """
    Test to check that OmeTifWriter correctly saves the dimensionality of the array input
    This assures that the target_tuple stays the same shape and is not transposed
    """
    def runTest(self):
        target_tuple = (2, 3, 4, 5)
        test_array = np.ones(target_tuple)

        self.writer.save(test_array)
        test_reader = omeTifReader.OmeTifReader(os.path.join(self.dir_path, 'img', 'ometiftest_output.ome.tif'))
        checked_array = test_reader.load()
        self.assertEqual(target_tuple, checked_array.shape)
