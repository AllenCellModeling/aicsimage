#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

import os
import unittest
import numpy as np

from aicsimage import io
from aicsimage.io import omeTifWriter, omeTifReader


class OmeTifWriterTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        io.init()
        cls.dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'img')
        cls.file = os.path.join(cls.dir_path, 'ometif_test_output.ome.tif')
        cls.image = np.random.rand(1, 40, 3, 128, 256)
        cls.writer = omeTifWriter.OmeTifWriter(cls.file, overwrite_file=True)
        if not os.path.isfile(cls.file):
            open(cls.file, 'a').close()

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file)
        io.close()

    """
    Test to check that OmeTifWriter saves arrays that are reflexive with OmeTifReader
    """
    def test_writerShapeComparison(self):
        self.writer.save(self.image)

        with omeTifReader.OmeTifReader(self.file) as test_output_reader:
            output = test_output_reader.load()

        self.assertEqual(output.shape, self.image.shape)

    """
    Test to check if save() will only accept 3, 4, 5 dimensions for data
    """
    def test_loadAssertionError(self):
        image_to_save = np.ones((1, 2, 3, 4, 5, 6))
        with self.assertRaises(Exception):
            self.writer.save(image_to_save)

    """
    Test to check if save() can overwrite a file
    """
    def test_overwriteFile(self):
        with omeTifWriter.OmeTifWriter(self.file, overwrite_file=True) as writer:
            writer.save(self.image)

    """
    Test to check if save() will raise error when user does not want to overwrite a file that exists
    """
    def test_dontOverwriteFile(self):
        with self.assertRaises(Exception):
            with omeTifWriter.OmeTifWriter(self.file) as writer:
                writer.save(self.image)
