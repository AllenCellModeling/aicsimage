#!/usr/bin/env python

# Author: Zach Crabtree zacharyc@alleninstitute.org

from cziReaderTest import *
from omeTifReaderTest import *
from omeTifWriterTest import *
from tifReaderTest import *
from pngWriterTest import *
from pngReaderTest import *
import unittest


def main():
    # czi tests
    czi_reader_test_suite = unittest.TestSuite()
    czi_reader_test_suite.addTest(CziLoadDimensionTestCase())
    czi_reader_test_suite.addTest(CziLoadImageDimensionsTestCase())
    # this test doesn't work if load() attains a 5 dim array
    czi_reader_test_suite.addTest(CziLoadComparisonLoadImageTestCase())

    # ome tif tests
    ome_tif_reader_test_suite = unittest.TestSuite()
    ome_tif_reader_test_suite.addTest(OmeTifLoadDimensionTestCase())
    ome_tif_reader_test_suite.addTest(OmeTifLoadImageDimensionTestCase())
    ome_tif_reader_test_suite.addTest(OmeTifLoadCompareLoadImageTestCase())

    ome_tif_writer_test_suite = unittest.TestSuite()
    ome_tif_writer_test_suite.addTest(OmeTifWriterShapeComparisonTestCase())
    ome_tif_writer_test_suite.addTest(OmeTifWriterDimensionTestCase())

    # tif tests
    tif_reader_test_suite = unittest.TestSuite()
    tif_reader_test_suite.addTest(TifLoadImageDimensionTestCase())
    tif_reader_test_suite.addTest(TifLoadDimensionTestCase())
    tif_reader_test_suite.addTest(TifLoadComparisonTestCase())

    # png tests
    png_reader_test_suite = unittest.TestSuite()
    png_reader_test_suite.addTest(PngReaderShapeComparisonTestCase())

    png_writer_test_suite = unittest.TestSuite()
    png_writer_test_suite.addTest(PngSaveComparisonTestCase())
    png_writer_test_suite.addTest(PngSaveImageComparisonTestCase())

    # combining into single test suite
    # comment out the individual suites below to save run time, instead of the test cases above
    complete_test_suite = unittest.TestSuite()
    complete_test_suite.addTest(czi_reader_test_suite)
    complete_test_suite.addTest(ome_tif_reader_test_suite)
    complete_test_suite.addTest(ome_tif_writer_test_suite)
    complete_test_suite.addTest(tif_reader_test_suite)
    complete_test_suite.addTest(png_reader_test_suite)
    complete_test_suite.addTest(png_writer_test_suite)

    unittest.TextTestRunner(verbosity=2).run(complete_test_suite)

main()
