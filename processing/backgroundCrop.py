# Author: Evan Wiederspan <evanw@alleninstitute.org>
import numpy as np


def crop(img, val=0, axis=(-3, -2, -1), padding=0, get_slices=False):
    """
    Crops an image to remove the background color val
    :param img: numpy array to crop
    :param val: value to crop out. default is 0
    :param axis: tuple or list of axis indices to crop along. Can be either positive or negative values.
    Negative values will be from the end of the array as opposed to the start. By default, it crops along the last
    three axes
    :param padding: integer. Specifies how much of the background val to leave in the output. Will be applied 
    on all axis that are being cropped
    :param get_slices: boolean. If true, will return the slice indices that were taken out of the original image
    along with the cropped image. Default is true
    :return: either the cropped numpy array, or a tuple containing the cropped array and a tuple of slices taken
    out of the original data
    """
    try:
        ndim = img.ndim
    except AttributeError:
        raise ValueError("img must be a numpy array")
    # check that padding is a positive integer
    if not isinstance(padding, int) or padding < 0:
        raise ValueError('padding must be a positive integer')
    # map of index of axis to crop to tuple of endpoints (min, max)
    ends_map = {a: [0, img.shape[a]] for a in range(ndim)}
    try:
        for i in axis:
            # axis to search
            try:
                a = i if i >= 0 else ndim + i
            except TypeError:
                # if i isn't a number
                raise ValueError("axis must only contain integers")
            if a not in ends_map:
                raise ValueError("Invalid axis index: " + str(a))
            axis_slice = [slice(None, None)] * ndim
            axis_length = img.shape[a] - 1
            # loop from front to find min
            for s_i in range(axis_length):
                axis_slice[a] = s_i
                if not np.all(np.isnan(img[axis_slice]) if np.isnan(val) else img[axis_slice] == val):
                    ends_map[a][0] = max(s_i - padding, 0)
                    break
            # loop from back to find max
            for s_i in range(axis_length, 0, -1):
                axis_slice[a] = s_i
                if not np.all(np.isnan(img[axis_slice]) if np.isnan(val) else img[axis_slice] == val):
                    ends_map[a][1] = min(s_i + padding + 1, img.shape[a])
                    break
    except TypeError:
        # thrown if axis is not iterable
        raise ValueError("axis must be an iterable")
    crop_slices = tuple(slice(*ends_map[a]) for a in range(ndim))
    if get_slices:
        return (img[crop_slices].copy(), tuple(ends_map[a] for a in range(ndim)))
    else:
        return img[crop_slices].copy()
