# author: Zach Crabtree zacharyc@alleninstitute.org

import numpy as np
from scipy.ndimage.filters import gaussian_filter
from skimage.filters import threshold_otsu

def fill_nucleus_segmentation(cell_index_img, nuc_index_img, nuc_original_img):
    """
    This function is built to fill in the holes of the nucleus segmentation channel
    :param cell_index_img: A ZYX ndarray - represents the segmented image of all cell bodies
    :param nuc_index_img: A ZYX ndarray - represents the segmented image of all nuclei
    :param nuc_original_img: A ZYX ndarray - represents the original image of the nuclei channel
    :return: corrected_image: A ZYX ndarray - represents a corrected segmented image of the nuclei (all holes filled in)
    """
    for cell_value in range(1, cell_index_img.max()):
        # get indices of cell with cell_value as its ID
        cell_indices = np.where(cell_index_img == cell_value)
        # if a cell exists with this cell_value
        if len(cell_indices[0]) > 0:
            z_indices, y_indices, x_indices = cell_indices[0], cell_indices[1], cell_indices[2]

            # creates buffer of 10 pixels/slices around the image, or the boundaries of the original image
            x_slice = slice(max(1, -10+min(x_indices)), min(10+max(x_indices), cell_index_img.shape[2]))
            y_slice = slice(max(1, -10+min(y_indices)), min(10+max(y_indices), cell_index_img.shape[1]))
            z_slice = slice(max(1, -10+min(z_indices)), min(10+max(z_indices), cell_index_img.shape[0]))

            cropped_nuc_im = nuc_original_img[z_slice, y_slice, x_slice]
            # crop and mask the whole cell segmentation
            cropped_cell_seg = cell_index_img[z_slice, y_slice, x_slice]
            cropped_cell_seg_mask = cropped_cell_seg == cell_value
            cropped_cell_seg[cropped_cell_seg_mask == False] = 0
            # crop and mask the nuclear segmentation
            cropped_nuc_seg = nuc_index_img[z_slice, y_slice, x_slice]
            cropped_nuc_seg_mask = cropped_nuc_seg == cell_value
            cropped_nuc_seg[cropped_nuc_seg_mask == True] = 0
            # this is a 3D Gaussian filter with size of [41, 41, 11]
            # corresponds to a sigma array of [41, 41, 11]/(4*sqrt(2*log(2)))
            filter_correction = gaussian_filter(cropped_cell_seg, [41, 41, 11])
            cropped_filtered_nuc_im = np.divide(gaussian_filter(cropped_nuc_im, [41, 41, 11]), filter_correction)
            crop_max = cropped_filtered_nuc_im.max()
            crop_min = cropped_filtered_nuc_im.min()

            im_threshold = np.multiply(cropped_filtered_nuc_im[cropped_filtered_nuc_im > 1.1], threshold_otsu(cropped_filtered_nuc_im[cropped_filtered_nuc_im > 0]))
