#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest
import numpy as np
import tifffile
from aicsimagetools import omeTifWriter
from aicsimagetools import omeTifReader


class SetUpTestCase(unittest.TestCase):
    def setUp(self):
        self.writer = omeTifWriter.OmeTifWriter(os.path.join('img', 'ometiftest_output.ome.tif'))
        self.reader = omeTifReader.OmeTifReader(os.path.join('img', 'img40_1.ome.tif'))


class OmeTifWriterComparisonTest(SetUpTestCase):
    def runTest(self):
        comparison_array = self.reader.load()
        self.writer.save(comparison_array)
        output_reader = omeTifReader.OmeTifReader(os.path.join('img', 'ometiftest_output.ome.tif'))
        writer_output_array = output_reader.load()
        self.assertEqual(comparison_array.shape, writer_output_array.shape)


