# Author: Evan Wiederspan <evanw@alleninstitute.org>

import numpy as np
from .backgroundCrop import crop, get_edges
from scipy.ndimage.measurements import center_of_mass


def _shape_to(img, out_shape, val=0):
    """
    Pads or crops an image to make it the same size as out_shape
    Applied equally on both ends of axes to keep the center of the image the same
    """
    try:
        if img.ndim != len(out_shape):
            raise ValueError("Out shape has wrong number of dimensions")
    except AttributeError:
        raise ValueError("img must be a numpy array")
    # image to be returned
    out = np.empty(out_shape, dtype=int)
    # slices taken from input image
    in_slices = [[None, None] for _ in range(img.ndim)]
    # slices of where to apply input image to output
    out_slices = [[None, None] for _ in range(len(out_shape))]
    for a in range(img.ndim):
        axis_slices = [slice(None, None)] * img.ndim
        diff = img.shape[a] - out_shape[a]
        left_edge = diff // 2
        # cropping, take a slice from the input image
        if img.shape[a] >= out_shape[a]:
            in_slices[a] = [left_edge, img.shape[a] - (diff - left_edge)]
        # padding, apply whole input to smaller area of output
        else:
            # fill in new padding with val
            axis_slices[a] = slice(0, left_edge)
            out[axis_slices] = val
            axis_slices[a] = slice(out_shape[a] - (diff - left_edge), None)
            out[axis_slices] = val
            out_slices[a] = [left_edge, out_shape[a] - (diff - left_edge)]
    in_slices = [slice(*s) for s in in_slices]
    out_slices = [slice(*s) for s in out_slices]
    out[out_slices] = img[in_slices]
    return out


def crop_all(images):
    """
    Crop all images by the same amount. The amount to crop will be calculated
    so that an equal amount is removed on both sides of each axis to keep the center of mass
    in the center
    """
    try:
        shape = images[0].shape
        if len(shape) != 4:
            raise ValueError("images must be a list of 4d numpy arrays")
        edges = [get_edges(img) for img in images]
    except (IndexError, AttributeError, TypeError):
        raise ValueError("images must be a list of 4d numpy arrays")
    slices = [slice(None, None)]
    for axis_index, axis_edges in enumerate(zip(*edges), start=1):
        # axis_edges is a list of 2 element lists containing the endpoints
        # for each image in a single axis
        axis_length = shape[axis_index]
        axis_min = min(a[0] for a in axis_edges)
        axis_max = max(a[1] for a in axis_edges)
        # crop each side by the same amount
        slice_amount = min(axis_min, axis_length - axis_max)
        slices.append(slice(slice_amount, axis_length - slice_amount))
    return [img[slices] for img in images]


def center_image(image, moves=None, fill=0):
    """
    Aligns image based on the center of mass.
    :param image: CZYX image as a numpy array that will be centered by adding padding
    :param moves: tuple of integers, returned from a previous call of this function. If specified, will move the image by
    that amount instead of recalculating it (used to move multiple images by the same amount)
    :param fill: Value to use when adding padding. Default is 0
    :return: If moves is not specified, a tuple containing the centered image and the moves tuple to be provided to
    future function calls. If moves is specified, it returns just the moved image
    """
    try:
        if image.ndim != 4:
            raise ValueError("image must be a 4d numpy array")
    except AttributeError:
        raise ValueError("image must be a 4d numpy array")
    return_tuple = moves is None
    if moves is None:
        # calculate how far off center the image is in each direction
        # slice with [1:] to skip the color axis
        moves = tuple(int(m) - (l // 2) for l, m in zip(image.shape[1:], center_of_mass(image)[1:]))
    # add padding to image to put center of mass in center
    padding = [(0, 0)] + [(-p, 0) if p < 0 else (0, p) for p in moves]
    if not isinstance(moves, tuple):
        raise ValueError("Incorrect format for 'moves', should be tuple returned from previous function call")
    if return_tuple:
        return (np.pad(image, padding, "constant"), moves)
    else:
        return np.pad(image, padding, "constant")