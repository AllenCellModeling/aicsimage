# Author: Evan Wiederspan <evanw@alleninstitute.org>
import numpy as np


def _mean_sub(img):
    """
    Subtract the mean value from the whole image
    """
    res = img - np.mean(img)
    res[res < 0] = 0
    return res


def _most_common(img):
    """
    Subtract the most common value from the whole image
    """
    # this may need to be changed, only really works if the array is all integers
    histo, bin_edges = np.histogram(img, bins=256)
    mode = bin_edges[np.argmax(histo)]
    res = img - mode
    res[res < 0] = 0
    return res


def _median(img):
    """
    Subtract the median value
    """
    res = img - np.sort(img.flatten())[img // 2]
    res[res < 0] = 0
    return res


def background_sub(img, mask=None, method="mean"):
    # apply mask if there is one
    if mask is not None:
        img = img[mask]
    if method == "mean":
        return _mean_sub(img)
    elif method == "common":
        return _most_common(img)
    elif method == "median":
        return _median(img)
    else:
        raise ValueError("Invalid method")
