# Author Evan Wiederspan <evanw@alleninstitute.org>

import numpy as np
from scipy.ndimage.interpolation import rotate
from math import ceil
from backgroundCrop import crop


def get_major_minor_axis(img):
    """
    Finds the major and minor axis as 3d vectors of the passed in image
    :param img: CZYX numpy array
    :return: tuple containing two numpy arrays representing the major and minor axis as 3d vectors
    """
    z, y, x = np.nonzero(np.mean(img, axis=0))
    coords = np.stack([x - np.mean(x), y - np.mean(y), z - np.mean(z)])
    # eigenvectors and values of the covariance matrix
    evals, evecs = np.linalg.eig(np.cov(coords))
    # return largest and smallest eigenvectors (major and minor axis)
    order = np.argsort(evals)
    return (evecs[:, order[-1]], evecs[:, order[0]])


def unit_vector(v):
    """
    Return unit vector of v
    :param v: vector as numpy array
    :return: unit vector of same length as v
    """
    try:
        return v / np.linalg.norm(v)
    except ZeroDivisionError:
        return np.array([0] * v.ndim)


def angle_between(v1, v2):
    """
    Finds angle between two 2d vectors
    :param v1: first vector as a numpy array
    :param v2: second vector as a numpy array
    :return: angle between v1 and v2 in degrees
    """
    if getattr(v1, 'ndim', 0) != 1 or getattr(v2, 'ndim', 0) != 1:
        raise ValueError("v1 and v2 must be 1d numpy arrays")
    dot_prod = np.dot(unit_vector(v1), unit_vector(v2))
    # happens if of one the passed in vectors has length 0
    if np.isnan(dot_prod):
        return 0
    return np.degrees(np.arccos(dot_prod))


def align_major(img, axis="zyx", reshape=False):
    """
    Rotates a CZYX image so that its major, minor-ish, and minor axis are aligned with
    the axis specified in the 'axis' parameter
    E.g. axis='zyx' will align the major axis of the image to align with the z axis
    and the minor to align with the x axis
    :param img: a CZYX image as a 4d numpy array that will be rotated
    :param axis: string, that must be an arrangement of 'xyz'
    The major axis will be aligned with the first one, the minor with the last one.
    'zyx' by default
    :param reshape: boolean. If True, the output will be resized to ensure that no data
    from img is lost. If False, the output will be the same size as the input, with potential to
    lose data that lies outside of the input shape after rotation
    :return: A CZYX image as a 4d numpy array containing the rotated input
    """
    if getattr(img, 'ndim', 0) != 4:
        raise ValueError('img must be a 4d numpy array')
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if not isinstance(axis, str) or len(axis) != 3 or not all(a in axis_map for a in axis):
        raise ValueError("axis must be an arrangement of 'xyz'")
    axis_list = [axis_map[a] for a in axis]
    # unit vectors for x, y, and z axis
    axis_vectors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    # slices for selecting yz, xz, and xy components from vectors
    slices = (slice(1, 3), slice(0, 3, 2), slice(0, 2))
    rotate_axis = ((1, 2), (1, 3), (2, 3))
    # index of the major axis (0, 1, or 2)
    maj_axis_i = axis_list[0]
    maj_axis = axis_vectors[axis_list[0]]
    min_axis = axis_vectors[axis_list[-1]]
    img_maj_axis, img_min_axis = get_major_minor_axis(img)
    # rotate around other two axis (e.g if aligning major to Z axis, rotate around Y and X to get there)
    out = img.copy()
    for a in range(3):
        if a == maj_axis_i:
            # final rotation goes around major axis to align the minor axis properly
            angle = angle_between(min_axis[slices[maj_axis_i]], img_min_axis[slices[maj_axis_i]])
        else:
            angle = angle_between(maj_axis[slices[a]], img_maj_axis[slices[a]])
        out = rotate(out, angle, reshape=reshape, order=1, axes=rotate_axis[a], cval=(np.nan if reshape else 0))
    if reshape:
        # cropping necessary as each resize makes the image bigger
        # np.nan used as fill value when reshaping in order to make cropping easy
        out = crop(out, np.nan)
        out[np.isnan(out)] = 0
    return out
