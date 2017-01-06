#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest
import numpy as np
import aicsimagetools
from aicsimagetools import omeTifWriter
from aicsimagetools import omeTifReader


class OmeTifWriterTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        aicsimagetools.init()
        cls.dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'img')
        cls.image = np.random.rand(1, 40, 3, 128, 256)
        cls.writer = omeTifWriter.OmeTifWriter(os.path.join(cls.dir_path, 'ometif_test_output.ome.tif'))

    @classmethod
    def tearDownClass(cls):
        aicsimagetools.close()

    """
    Test to check that OmeTifWriter saves arrays that are reflexive with OmeTifReader
    """
    def test_writerShapeComparison(self):
        self.writer.save(self.image, overwrite_file=True)

        with omeTifReader.OmeTifReader(os.path.join(self.dir_path, 'ometif_test_output.ome.tif')) as test_output_reader:
            output = test_output_reader.load()

        self.assertEqual(output.shape, self.image.shape)

    """
    Test to check if save() will only accept 3,4,5 dimensions for data
    """
    def test_loadAssertionError(self):
        image_to_save = np.ones((1, 2, 3, 4, 5, 6))
        with self.assertRaises(AssertionError):
            self.writer.save(image_to_save, overwrite_file=True)

    """
        Test to check if save() can overwrite a file
        """

    def test_overwriteFile(self):
        with omeTifWriter.OmeTifWriter(os.path.join(self.dir_path, 'ometif_test_output.ome.tif')) as writer:
            writer.save(self.image, overwrite_file=True)

    """
    Test to check if save() will raise error when user does not want to overwrite a file that exists
    """

    def test_dontOverwriteFile(self):
        with self.assertRaises(Exception):
            with omeTifWriter.OmeTifWriter(os.path.join(self.dir_path, 'ometif_test_output.ome.tif')) as writer:
                writer.save(self.image)
