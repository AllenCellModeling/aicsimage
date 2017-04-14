import unittest
import numpy as np
from np.random import randint
from processing.backgroundSub import background_sub as bg_sub


class BackgroundSubTestGroup(unittest.TestCase):

    def test_positiveOutput(cls):
        methods = ["mean", "median", "common"]
        # perform subtraction on random input with a random method
        # to ensure that no values in the output are ever negative
        for _ in range(5):
            method = methods[randint(len(methods))]
            test = bg_sub(randint(255, size=(3, 10, 10, 10), method=method))
            self.assertTrue(np.all(test >= 0), "No negative values for {} method".format(method))

    def test_methodInput(self):
        with self.assertRaises(ValueError, msg="Invalid method check"):
            bg_sub(self.testImage, method="fake")

    def test_mean(self):
        n = 10
        testImage = np.arange(n)
        res = bg_sub(testImage, method="mean")
        self.assertTrue(np.max(res) == n - np.mean(testImage), "Mean background subtraction")

    def test_median(self):
        n = 10
        testImage = np.arange(n)
        res = bg_sub(testImage, method="median")
        self.assertTrue(np.max(res) == n - n // 2, "Median background subtraction")

    def test_common(self):
        n = 10
        c_val = 5
        testImage = np.arange(n)
        testImage[4:7] = c_val
        res = bg_sub(testImage, method="common")
        self.assertTrue(np.max(res) == n - c_val, "Common background subtraction")
