# Author: Evan Wiederspan <evanw@alleninstitute.org>

import numpy as np
import unittest
from processing.backgroundCrop import crop


class BackgroundCropTestGroup(unittest.TestCase):

    def test_cropInputs(self):
        testImage = np.zeros((3, 10, 10, 10))
        self.assertIsNotNone(crop(testImage), "Standard test")
        with self.assertRaises(ValueError, msg="Positive axis must be in range"):
            crop(testImage, axis=(1, 2, 10))
        with self.assertRaises(ValueError, msg="Negative axis must be in range"):
            crop(testImage, axis=(1, 2, -10))
        with self.assertRaises(ValueError, msg="Axis must be iterable"):
            crop(testImage, axis=0)

    def test_cropOutputs(self):
        testImage = np.zeros((3, 10, 10, 10))
        testImage[:, 3:6, 3:6, 3:6] = np.eye(3)
        self.assertEqual(crop(testImage, 2).shape, (3, 10, 10, 10), "Nothing cropped when crop value not found")
        self.assertEqual(crop(testImage), (3, 3, 3, 3), "Cropped output is in expected shape")

        cropped, slice_indices = crop(testImage, 0, get_slices=True)
        self.assertEqual(cropped.shape, (3, 3, 3, 3), "Cropped output is expected shape when returning slices")
        self.assertEqual(slice_indices, ([0, 10], [3, 6], [3, 6], [3, 6]), "Slice indices match expected values")
        self.assertEqual(crop(testImage, 0, (-2, -1)), (3, 10, 3, 3), "Crop only specified axes")
        self.assertEqual(crop(testImage, 0, tuple()), (3, 10, 10, 10), "Crop skipped when no axis specified")

        self.assertEqual(crop(testImage, 0, padding=1).shape, (3, 4, 4, 4), "Crops to expected shape with padding")
        self.assertEqual(crop(testImage, 0, padding=100).shape, (3, 10, 10, 10), "Crops correctly with large padding")
