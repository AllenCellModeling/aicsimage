# Author: Evan Wiederspan <evanw@alleninstitute.org>

import numpy as np
from backgroundCrop import crop, get_edges
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


def crop_all(images, axis=(-3, -2, -1)):
    """
    Crop all images by the same amount. The amount to crop will be calculated
    so that an equal amount is removed on both sides of each axis to keep the center of mass
    in the center
    :param images: List of images to crop. The images can be any shape or dimensionality but must
    all have the same shape
    :param axis: List of axis to crop along. Default is the last three axis (meant to correspond to ZYX)
    :return: List of cropped images, in the same order as they were passed in
    """
    try:
        if not isinstance(images, (type(tuple()), type([]))):
            raise ValueError("images must be an iterable")
        shape = images[0].shape
        if not all(img.shape == shape for img in images):
            raise ValueError("images must all have the same shape")
        edges = [get_edges(img, axis=axis) for img in images]
    except (IndexError, AttributeError, TypeError):
        raise ValueError("images must be a list of numpy arrays")
    slices = [[None, None] for _ in range(len(shape))]
    for axis_index, axis_edges in zip(axis, zip(*edges)):
        axis_length = shape[axis_index]
        # axis_edges is a list of 2 element lists containing the endpoints
        # for each image in a single axis
        axis_length = shape[axis_index]
        axis_min = min(a[0] for a in axis_edges)
        axis_max = max(a[1] for a in axis_edges)
        # crop each side by the same amount
        slice_amount = min(axis_min, axis_length - axis_max)
        slices[axis_index] = [slice_amount, axis_length - slice_amount]
    return [img[tuple(slice(*s) for s in slices)] for img in images]


def center_image(image, moves=None, axis=(-3, -2, -1), fill=0):
    """
    Aligns image based on the center of mass.
    :param image: Image as a numpy array that will be centered by adding padding. Can be any dimensionality
    :param moves: List of integers, returned from a previous call of this function. If specified, will move the image by
    that amount instead of recalculating it (used to move multiple images by the same amount)
    :param axis: Iterable containing the axis to center the image on. Order does not affect the output. Default is the last three
    axis (meant to be ZYX)
    :param fill: Value to use when adding padding. Default is 0
    :return: If moves is not specified, a tuple containing the centered image and the moves tuple to be provided to
    future function calls. If moves is specified, it returns just the moved image
    """
    if not isinstance(image, np.ndarray):
        raise ValueError("image must be a 4d numpy array")
    return_tuple = moves is None
    if moves is None:
        # calculate how far off center the image is in each direction
        com = center_of_mass(image)
        moves = [0] * image.ndim
        try:
            for a in axis:
                moves[a] = int(com[a]) - (image.shape[a] // 2)
        except IndexError:
            raise ValueError("Invalid axis")
    # add padding to image to put center of mass in center
    padding = [(-p, 0) if p < 0 else (0, p) for p in moves]
    if not isinstance(moves, list):
        raise ValueError("Incorrect format for 'moves', should be list returned from previous function call")
    if return_tuple:
        return (np.pad(image, padding, "constant", constant_values=fill), moves)
    else:
        return np.pad(image, padding, "constant", constant_values=fill)
