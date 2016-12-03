#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest
import numpy as np
from aicsimagetools import omeTifWriter
from aicsimagetools import omeTifReader


class OmeTifWriterTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'img')
        reader = omeTifReader.OmeTifReader(os.path.join(cls.dir_path, 'img40_1.ome.tif'))
        cls.sample_array = reader.load()
        reader.close()

    """
    Test to check that OmeTifWriter saves arrays that are reflexive with OmeTifReader
    """
    def test_writerShapeComparison(self):
        writer = omeTifWriter.OmeTifWriter(os.path.join(self.dir_path, 'ometiftest_output.ome.tif'))
        writer.save(self.sample_array)
        test_output_reader = omeTifReader.OmeTifReader(os.path.join(self.dir_path, 'ometiftest_output.ome.tif'))
        array_to_check = test_output_reader.load()
        self.assertEqual(array_to_check.shape, self.sample_array.shape)
        writer.close()
        test_output_reader.close()

    """
    Test to check that OmeTifWriter correctly saves the dimensionality of the array input
    This assures that the target_tuple stays the same shape and is not transposed
    """
    def test_writerDimensionTestCase(self):
        writer = omeTifWriter.OmeTifWriter(os.path.join(self.dir_path, 'ometiftest_output.ome.tif'))
        target_tuple = (2, 3, 4, 5)
        target_array = np.ones(target_tuple)
        writer.save(target_array)
        test_output_reader = omeTifReader.OmeTifReader(os.path.join(self.dir_path, 'ometiftest_output.ome.tif'))
        checked_array = test_output_reader.load()
        self.assertEqual(target_tuple, checked_array.shape)
        writer.close()
        test_output_reader.close()
