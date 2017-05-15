# author: Zach Crabtree zacharyc@alleninstitute.org

import numpy as np
from scipy.ndimage.filters import gaussian_filter
from skimage.filters import threshold_otsu
from scipy.ndimage.measurements import label
from skimage.measure import regionprops
from skimage import morphology
from aicsimage.io.omeTifWriter import OmeTifWriter

def keep_connected_components(image, low_threshold, high_threshold=None):

    if high_threshold is None:
        high_threshold = len(image)

    labels = label(image)
    object_areas = [ob_region.area for ob_region in regionprops(labels[0])]
    output = np.zeros(image.shape)

    if len(object_areas) > 1:
        indices = np.where(low_threshold < object_areas <= high_threshold)
        for index in indices:
            output = output or labels[0] == index
    else:
        output = image.copy()

    return output


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

    for cell_value in range(1, cell_index_img.max()):
        # get indices of cell with cell_value as its ID
        cell_indices = np.where(cell_index_img == cell_value)
        # if a cell exists with this cell_value
        if len(cell_indices[0]) > 0:
            z_indices, y_indices, x_indices = cell_indices[0], cell_indices[1], cell_indices[2]
            # creates buffer of 10 pixels/slices around the cell, or stops at the boundaries of the original image
            x_slice = slice(max(1, -10+min(x_indices)), min(10+max(x_indices), cell_index_img.shape[2]))
            y_slice = slice(max(1, -10+min(y_indices)), min(10+max(y_indices), cell_index_img.shape[1]))
            z_slice = slice(max(1, -10+min(z_indices)), min(10+max(z_indices), cell_index_img.shape[0]))
            # crop and mask the whole cell segmentation
            cropped_cell_seg = cell_index_img[z_slice, y_slice, x_slice].astype(np.float64)
            cropped_cell_seg[cropped_cell_seg != cell_value] = 0
            # crop and mask the nucleus channel
            output = nuc_original_img[z_slice, y_slice, x_slice]
            output[cropped_cell_seg != cell_value] = 0
            # filter the membrane segmentation channel
            cropped_cell_seg[cropped_cell_seg > 0] = gaussian_filter(cropped_cell_seg[cropped_cell_seg > 0], 41)
            # filter the nuclear channel
            output = gaussian_filter(output, [41, 41, 11])
            # this indexing assures that no values in output are divided by zero
            output[cropped_cell_seg > 0] /= cropped_cell_seg[cropped_cell_seg > 0]
            output[cropped_cell_seg == 0] = 0
            # threshold and mask to get the new nuclear segmentation
            otsu_threshold = threshold_otsu(output[output > 0])
            output[output <= otsu_threshold] = 0
            output[output > otsu_threshold] = 1
            OmeTifWriter("./img/segmentation/threshold.ome.tif", overwrite_file=True).save(output)

            # clean the images of objects and holes
            for z in range(output.shape[0]):
                output[z] = morphology.remove_small_objects(output[z].astype(np.int))
                output[z] = morphology.remove_small_holes(output[z].astype(np.int))
            OmeTifWriter("./img/segmentation/removal.ome.tif", overwrite_file=True).save(output)

            total_area = np.prod(output.shape)
            output = keep_connected_components(output,  total_area // 4, total_area * 2)


