# author: Zach Crabtree zacharyc@alleninstitute.org
from __future__ import print_function
import numpy as np
import math as m
from scipy.ndimage.filters import gaussian_filter
from skimage.filters import threshold_otsu
from scipy.ndimage.measurements import label
from skimage.measure import regionprops
from skimage import morphology
import os
import timeit

from aicsimage.io.omeTifWriter import OmeTifWriter

def keep_connected_components(image, low_threshold, high_threshold=None):

    if high_threshold is None:
        high_threshold = np.prod(image.shape)

    # label objects in image and get total number of objects detected
    labels, num_objects = label(image)
    output = np.zeros(image.shape)

    if num_objects > 1:
        # get the area of each object
        components = regionprops(labels)

        for component in components:
            if low_threshold < component.area <= high_threshold:
                output[labels == component.label] = 1
    else:
        output = image.copy()

    return output

# helpful debugging function
def _save_inter_image(image, index, name):
    file_path = os.path.join("img/segmentation", name + "_" + str(index) + ".ome.tif")
    OmeTifWriter(file_path, overwrite_file=True).save(image)

def fill_nucleus_segmentation(cell_index_img, nuc_original_img):
    """
    This function is built to fill in the holes of the nucleus segmentation channel
    :param cell_index_img: A ZYX ndarray - represents the segmented image of all cell bodies
    :param nuc_original_img: A ZYX ndarray - represents the original image of the nuclei channel
    :return: corrected_image: A ZYX ndarray - represents a corrected segmented image of the nuclei (all holes filled in)
    """
    # cast as float and normalize the input image
    nuc_original_img = nuc_original_img.astype(np.float64)
    original_max = np.max(nuc_original_img)
    original_min = np.min(nuc_original_img)
    nuc_original_img = (nuc_original_img - original_min) / (original_max - original_min) * 255
    total_out = np.zeros(nuc_original_img.shape)

    for cell_value in range(1, cell_index_img.max() + 1):
    # for cell_value in range(1, 5):
        # get indices of cell with cell_value as its ID
        cell_indices = np.where(cell_index_img == cell_value)
        # if a cell exists with this cell_value
        if len(cell_indices[0]) > 0:
            start_time = timeit.default_timer()
            print("Processing cell label " + str(cell_value) + "...", end="")
            z_indices, y_indices, x_indices = cell_indices[0], cell_indices[1], cell_indices[2]
            # creates buffer of 10 pixels/slices around the cell, or stops at the boundaries of the original image
            x_slice = slice(max(1, -10+min(x_indices)), min(10+max(x_indices), cell_index_img.shape[2]))
            y_slice = slice(max(1, -10+min(y_indices)), min(10+max(y_indices), cell_index_img.shape[1]))
            z_slice = slice(max(1, -10+min(z_indices)), min(10+max(z_indices), cell_index_img.shape[0]))
            # crop and mask the whole cell segmentation
            cropped_cell_seg = cell_index_img[z_slice, y_slice, x_slice].astype(np.float64).copy()
            cropped_cell_seg[cropped_cell_seg != cell_value] = 0
            nucleus_mask = cropped_cell_seg.copy()
            # _save_inter_image(cropped_cell_seg, cell_value, "cropped_cell_seg")
            # crop and mask the nucleus channel
            output = nuc_original_img[z_slice, y_slice, x_slice].copy()
            output[nucleus_mask != cell_value] = 0
            # _save_inter_image(output, cell_value, "cropped_nuc")
            # filter the membrane segmentation channel
            sigma = np.divide([41, 41, 11], (4*m.sqrt(2*m.log(2))))
            cropped_cell_seg = gaussian_filter(cropped_cell_seg, sigma)
            # filter the nuclear channel
            output = gaussian_filter(output, sigma)
            # _save_inter_image(output, cell_value, "filtered")
            # this indexing assures that no values in output are divided by zero
            output[cropped_cell_seg > 0] /= cropped_cell_seg[cropped_cell_seg > 0]
            output[cropped_cell_seg == 0] = 0
            # _save_inter_image(output, cell_value, "corrected")
            # threshold and mask to get the new nuclear segmentation
            if len(output[output > 0]) > 0:
                otsu_threshold = threshold_otsu(output[output > 0])
                output[output <= otsu_threshold] = 0
                output[output > otsu_threshold] = 1
                # _save_inter_image(output, cell_value, "threshold")

                # clean the images of objects and holes
                output = morphology.remove_small_objects(output.astype(np.int))
                # TODO does this next call have to recast output as int?
                output = morphology.remove_small_holes(output.astype(np.int))
                # output needs to be recast as int, because the morphology methods above return boolean arrays
                output = output.astype(np.int)
                # _save_inter_image(output, cell_value, "removal")
                # get the total volume and ignore components less than a quarter of that volume
                total_volume = np.count_nonzero(output)
                output = keep_connected_components(output,  total_volume // 4, total_volume * 2)
                # _save_inter_image(output, cell_value, "connected_components")
                # change boolean value back to original segmentation value
                output *= cell_value
                # mask the nucleus inside the cell membrane segmentation again
                output[nucleus_mask != cell_value] = 0
                total_out[z_slice, y_slice, x_slice] += output
                _save_inter_image(total_out, cell_value, "total_out")
            elapsed_time = timeit.default_timer() - start_time
            print("done - elapsed time: " + str(elapsed_time) + " seconds")
    return total_out

