# author: Zach Crabtree zacharyc@alleninstitute.org

import numpy as np

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
            y_index, x_index, z_index = np.unravel_index(cell_index_img.shape, cell_indices)



