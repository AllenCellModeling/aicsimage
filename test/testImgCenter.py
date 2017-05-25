# Author: Evan Wiederspan <evanw@alleninstitute.org>
import unittest
import numpy as np
from aicsimage.processing.imgCenter import get_edges, crop_all, center, get_center_moves
from random import sample, randrange
from scipy.ndimage.measurements import center_of_mass


class ImgCenterTestGroup(unittest.TestCase):

    def getRandTest(self):
        """
        Helper function to get a random test image for centering testing
        """
        test = np.zeros((3, 10, 10, 10))
        moves = [0] + [randrange(-3, 4) for _ in range(3)]
        # create random 3 x 3 x 3 cube of 1's somewhere in the test image
        test[[slice(None, None)] + [slice(4 + m, 7 + m) for m in moves[1:]]] = 1
        return (test, moves)

    def test_getEdgesInput(self):
        with self.assertRaises(ValueError, msg="Must take in a numpy array"):
            get_edges([[[[1]]]])

    def test_getCenterCalc(self):
        test, moves = self.getRandTest()
        calc_moves = get_center_moves(test)
        self.assertEqual(moves, calc_moves, "Calculated moves {} should equal {}".format(calc_moves, moves))

    def test_imgCenterMoves(self):
        test = self.getRandTest()[0]
        moves = get_center_moves(test)
        res = center([test, test], moves=moves)
        self.assertTrue(np.array_equal(*res), "Should move multiple images the same amount")

    def test_imgCenterInputs(self):
        test = self.getRandTest()[0]
        moves = get_center_moves(test)
        moves += [0]
        with self.assertRaises(ValueError, msg="Requires a valid moves object"):
            center(test, moves)
        with self.assertRaises(ValueError, msg="Images must be the shame shape"):
            center([np.ones((3, 10, 10, 10)), np.ones((3, 5, 5, 5))], moves)

    def test_cropAllInputs(self):
        with self.assertRaises(ValueError, msg="crop_all requires an iterable as input"):
            crop_all(self.getRandTest()[0])
        with self.assertRaises(ValueError, msg="axis must be in range"):
            crop_all([self.getRandTest()[0] for _ in range(3)], axis=(-3, -2, 5))
        with self.assertRaises(ValueError, msg="Image shapes must be equal"):
            images = [self.getRandTest()[0] for _ in range(2)] + np.empty([randrange(1, 10) for _ in range(4)])
            crop_all(images)

    def test_cropAllOutSize(self):
        test_images = [self.getRandTest()[0] for _ in range(3)]
        out_images = crop_all(test_images)
        shape = out_images[0].shape
        self.assertTrue(all(shape == img.shape for img in out_images[1:]), "Images are same size after cropping")

    def test_cropAllAxis(self):
        for t in range(3):
            test_images = [self.getRandTest()[0] for _ in range(3)]
            a = randrange(1, 4)
            axis = [1, 2, 3]
            del axis[a - 1]
            out_images = crop_all(test_images, axis=axis)
            self.assertTrue(test_images[0].shape[a] == out_images[0].shape[a], "Does not crop on non-specified axis")

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
