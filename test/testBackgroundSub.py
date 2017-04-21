import unittest
import numpy as np
from processing.backgroundSub import background_sub as bg_sub


class BackgroundSubTestGroup(unittest.TestCase):

    def test_positiveOutput(self):
        methods = ["mean", "median", "common"]
        # perform subtraction on random input with a random method
        # to ensure that no values in the output are ever negative
        for _ in range(5):
            method = methods[np.random.randint(len(methods))]
            test = bg_sub(np.random.randint(255, size=(3, 10, 10, 10)), method=method)
            self.assertTrue(np.all(test >= 0), "No negative values for {} method".format(method))

    def test_methodInput(self):
        with self.assertRaises(ValueError, msg="Invalid method check"):
            bg_sub(np.ones((3, 5, 5, 5)), method="fake")

    def test_mean(self):
        n = 9
        testImage = np.arange(n + 1)
        res = bg_sub(testImage, method="mean")
        self.assertTrue(np.max(res) == n - np.mean(testImage), "Mean background subtraction")

    def test_median(self):
        n = 9
        testImage = np.arange(n + 1)
        res = bg_sub(testImage, method="median")
        self.assertTrue(np.max(res) == n - (n + 1) // 2, "Median background subtraction")

    def test_common(self):
        n = 9
        c_val = 5
        testImage = np.arange(n + 1)
        testImage[4:7] = c_val
        res = bg_sub(testImage, method="common")
        self.assertTrue(np.max(res) == n - c_val, "Common background subtraction")

    def test_mask(self):
        # test masking on random method
        method = ["mean", "common", "median"][np.random.randint(3)]
        testImage = np.random.random((3, 10, 10, 10))
        testImage[:, 1:9, 1:9, 1:9] = 1
        mask = testImage != 1
        res = bg_sub(testImage, mask=mask, method=method)
        self.assertTrue(np.any(res[mask] == 0), "Some zeroed value outside of mask")
        self.assertTrue(np.all(res[~mask] == 1), "Area inside mask is untouched")
