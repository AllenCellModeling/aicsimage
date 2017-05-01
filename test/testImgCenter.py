# Author: Evan Wiederspan <evanw@alleninstitute.org>
import unittest
import numpy as np
from aicsimage.processing.imgCenter import get_edges, crop_all, center_image
from random import sample, randrange
from scipy.ndimage.measurements import center_of_mass


class ImgCenterTestGroup(unittest.TestCase):

    def getRandTest(self):
        """
        Helper function to get a random test image for centering testing
        """
        test = np.zeros((3, 10, 10, 10))
        moves = tuple(randrange(-3, 4) for _ in range(3))
        # create random 3 x 3 x 3 cube of 1's somewhere in the test image
        test[[slice(None, None)] + [slice(4 + m, 7 + m) for m in moves]] = 1
        return (test, moves)

    def test_getEdgesInput(self):
        with self.assertRaises(ValueError, msg="Must take in a numpy array"):
            get_edges([[[[1]]]])

    def test_imgCenterCalc(self):
        test, moves = self.getRandTest()
        res, res_moves = center_image(test)
        self.assertEqual(moves, res_moves, "Calculated moves {} should equal {}".format(res_moves, moves))

    def test_imgCenterMoves(self):
        test = self.getRandTest()[0]
        calc_res, moves = center_image(test)
        move_res = center_image(test, moves=moves)
        self.assertTrue(np.all(calc_res == move_res), "Calculated image should equal moved image")

    def test_cropAllInputs(self):
        with self.assertRaises(ValueError, msg="crop_all requires an iterable as input"):
            crop_all(self.getRandTest()[0])

    def test_cropAllOutSize(self):
        test_images = [self.getRandTest()[0] for _ in range(3)]
        out_images = crop_all(test_images)
        shape = out_images[0].shape
        self.assertTrue(all(shape == img.shape for img in out_images[1:]), "Images are same size after cropping")

    def test_cropAllOutCOM(self):
        test_images = [self.getRandTest()[0] for _ in range(randrange(2, 6))]
        # mark center of each image
        # after cropping, each mark should remain in the center
        for img in test_images:
            img[0, 5, 5, 5] = 2
        out_images = crop_all(test_images)
        for img in out_images:
            # get point where mark is after cropping
            mark = np.array(np.where(img == 2)).flatten()
            self.assertTrue(all(float(mark) / length == 0.5 for mark, length in
                            zip(mark[1:], img.shape[1:])), "Mark remains at midpoint after cropping")
