#!/usr/bin/env python

# authors: Dan Toloudis danielt@alleninstitute.org
#          Zach Crabtree zacharyc@alleninstitute.org

from __future__ import print_function
import numpy as np
import skimage.transform as t
import math as m

z_axis_index = 0
_cmy = [[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]]

def get_thresholds(image, **kwargs):
    """
    This function finds thresholds for an image in order to reduce noise and bring up the peak contrast

    :param image: CYX-dimensioned image
    :param kwargs:
        "border_percent" : how much of the corners to ignore when calculating the threshold. Sometimes corners can be unnecessarily bright
                           default = .1
        "max_percent" : how much to ignore from the top intensities of the image
                        default = .998
        "min_percent" : what proportion of the bottom intensities of the image will be factored out
                        default = .40
    :return: tuple of float values, the lower and upper thresholds of the image
    """
    border_percent = .1 if not kwargs.has_key("border_percent") else float(kwargs["border_percent"])
    max_percent = .998 if not kwargs.has_key("max_percent") else float(kwargs["max_percent"])
    min_percent = .40 if not kwargs.has_key("min_percent") else float(kwargs["min_percent"])

    # expects CYX
    # using this allows us to ignore the bright corners of a cell image
    im_width = image.shape[2]
    im_height = image.shape[1]
    left_bound = int(m.floor(border_percent * im_width))
    right_bound = int(m.ceil((1 - border_percent) * im_width))
    bottom_bound = int(m.floor(border_percent * im_height))
    top_bound = int(m.ceil((1 - border_percent) * im_height))
    cut_border = image[:, left_bound:right_bound, bottom_bound:top_bound]

    immin = cut_border.min()
    immax = cut_border.max()
    histogram, bin_edges = np.histogram(image, bins=256, range=(immin, immax))
    total_cut = 0
    total_pixels = sum(histogram)
    lower_threshold = 0
    for i in range(len(histogram)):
        column = histogram[i]
        total_cut += column
        if total_cut >= total_pixels * min_percent:
            lower_threshold = bin_edges[i]
            break

    upper_threshold = np.max(cut_border) * max_percent

    return lower_threshold, upper_threshold


def resize_cyx_image(image, new_size):
    """
    This function resizes a CYX image.

    :param image: CYX ndarray
    :param new_size: tuple of shape of desired image dimensions in (C, Y, X)
    :return: image with shape of new_shape with image data
    """
    image = image.transpose((2, 1, 0))
    scaling = (float(image.shape[1]) / new_size[1])
    if scaling < 1:
        scaling = 1.0/scaling
        im_out = t.pyramid_expand(image, upscale=scaling)
    elif scaling > 1:
        im_out = np.asarray(t.pyramid_reduce(image, downscale=scaling))
    else:
        im_out = image
    im_out = im_out.transpose((2, 0, 1))
    return im_out


def mask_image(image, mask):
    """
    This function eliminates all data in the image where mask = 0

    :param image: an ndarray
    :param mask: a boolean ndarray with the same shape as image
    :return: an ndarray with the same shape as image
    """
    im_masked = np.multiply(image, mask > 0)
    return im_masked


def create_projection(image, axis, method='max', **kwargs):
    """
    This function creates a 2D projection out of an n-dimensional image.

    :param image: ZCYX array
    :param axis: the axis that the projection should be performed along
    :param method: the method that will be used to create the projection
                   Options: ["max", "mean", "sum", "slice", "sections"]
                   - max will look through each axis-slice, and determine the max value for each pixel
                   - mean will look through each axis-slice, and determine the mean value for each pixel
                   - sum will look through each axis-slice, and sum all pixels together
                   - slice will take the pixel values from the middle slice of the stack
                   - sections will split the stack into proj_sections number of sections, and take a
                   max projection for each.
    :param kwargs:
    :return:
    """
    slice_index = 0 if not kwargs.has_key("slice_index") else int(kwargs["slice_index"])
    sections = 3 if not kwargs.has_key("sections") else int(kwargs["sections"])

    if method == 'max':
        image = np.max(image, axis)
    elif method == 'mean':
        image = np.mean(image, axis)
    elif method == 'sum':
        image = np.sum(image, axis)
    elif method == 'slice':
        image = image[slice_index]
    elif method == 'sections':
        separator = int(m.floor(image.shape[0] / sections))
        # stack is a 2D YX im
        stack = np.zeros(image[0].shape)
        for i in range(sections - 1):
            bottom_bound = separator * i
            top_bound = separator * (i + 1)
            section = np.max(image[bottom_bound:top_bound], axis)
            stack += section
        stack += np.max(image[separator * sections - 1:])

        return stack
    # returns 2D image, YX
    return image


def arrange(projz, projx, projy, sx, sy, sz, rescale_inten=True):
    # assume all images are shape [x,y,3]
    # do stuff and return big image
    shZ = projz.shape
    shX = projx.shape
    shY = projy.shape
    assert (len(shZ) == len(shY) == len(shX) == 3)

    im_all = np.zeros(np.hstack((sx + sz, sy + sz, 3)))
    # imz is xXy
    im_all[0:sx, sz:] = projz
    # imy is zXx (so transpose it)
    im_all[0:sx, 0:sz] = np.transpose(projy, (1, 0, 2))
    # imx is zXy
    im_all[sx:, sz:] = projx

    if rescale_inten:
        im_all /= np.max(im_all.flatten())

    return im_all


def subtract_noise_floor(image, bins=256):
    # image is a 3D ZYX image
    immin = image.min()
    immax = image.max()
    hi, bin_edges = np.histogram(image, bins=bins, range=(max(1, immin), immax))
    # index of tallest peak in histogram
    peakind = np.argmax(hi)
    # subtract this out
    subtracted = image.astype(np.float32)
    subtracted -= bin_edges[peakind]
    # don't go negative
    subtracted[subtracted < 0] = 0
    return subtracted


class ThumbnailGenerator:
    """

    This class is used to generate thumbnails for 4D CZYX images.

    Example:
        generator = ThumbnailGenerator()
        for image in image_array:
            thumbnail = generator.make_thumbnail(image)

    """

    def __init__(self, colors=_cmy, size=128, channel_indices=[0, 1, 2], mask_channel_index=5, **kwargs):
        """
        :param colors: The color palette that will be used to color each channel. The default palette
                       colors the membrane channel cyan, structure with magenta, and nucleus with yellow.
                       Keep color-blind acccessibility in mind.

        :param size: This constrains the image to have the X or Y dims max out at this value, but keep
                     the original aspect ratio of the image.

        :param channel_indices: An array of channel indices to represent the three main channels of the cell

        :param mask_channel_index: The index for the segmentation channel in image that will be used to mask the thumbnail

        :param kwargs:
            "layering" : The method that will be used to layer each channel's projection over each other.
                         Options: ["superimpose", "alpha-blend"]
                         - superimpose will overwrite pixels on the final image as it layers each channel
                         - alpha-blend will blend the final image's pixels with each new channel layer

            "projection" : The method that will be used to generate each channel's projection. This is done
                           for each pixel, through the z-axis
                           Options: ["max", "slice", "sections"]
                           - max will look through each z-slice, and determine the max value for each pixel
                           - slice will take the pixel values from the middle slice of the z-stack
                           - sections will split the zstack into proj_sections number of sections, and take a
                             max projection for each.

            "proj_sections" : The number of sections that will be used to determine projections, if projection="sections"
        """

        layering = "alpha-blend" if not kwargs.has_key("layering") else kwargs["layering"]
        projection = "max" if not kwargs.has_key("projection") else kwargs["projection"]
        proj_sections = 3 if not kwargs.has_key("proj_sections") else kwargs["proj_sections"]

        assert len(colors) == 3 and len(colors[0]) == 3
        self.colors = colors

        self.size = size
        self.memb_index = channel_indices[0]
        self.struct_index = channel_indices[1]
        self.nuc_index = channel_indices[2]
        self.channel_indices = channel_indices
        self.mask_channel_index = mask_channel_index

        assert layering == "superimpose" or layering == "alpha-blend"
        self.layering_mode = layering

        assert projection == "slice" or projection == "max" or projection == "sections"
        self.projection_mode = projection
        self.proj_sections = proj_sections

    def _get_output_shape(self, im_size):
        """
        This method will take in a 3D ZYX shape and return a 3D XYC of the final thumbnail

        :param im_size: 3D ZYX shape of original image
        :return: CYX dims for a resized thumbnail where the maximum X or Y dimension is the one specified in the constructor.
        """
        # size down to this edge size, maintaining aspect ratio.
        max_edge = self.size
        # keep same number of z slices.
        shape_out = np.hstack((im_size[0],
                               max_edge if im_size[1] > im_size[2] else max_edge * im_size[1] / im_size[2],
                               max_edge if im_size[1] < im_size[2] else max_edge * im_size[2] / im_size[1]
                               ))
        return 3, shape_out[2], shape_out[1]

    def _layer_projections(self, projection_array, mask_array):
        """
        This method will take in a list of 2D XY projections and layer them according to the method specified in the constructor

        :param projection_array: list of 2D XY projections (for each channel of a cell image)
        :return: single 3D XYC image where C is RGB values for each pixel
        """
        # array cannot be empty or have more channels than the color array
        assert projection_array
        assert len(projection_array) == len(self.colors)
        layered_image = np.zeros((projection_array[0].shape[0], projection_array[0].shape[1], 4))

        for i in range(len(projection_array)):
            projection = projection_array[i]
            # normalize channel projection
            projection /= np.max(projection)
            assert projection.shape == projection_array[0].shape
            # 4 channels - rgba
            rgb_out = np.expand_dims(projection, 2)
            rgb_out = np.repeat(rgb_out, 4, 2).astype('float')
            # inject color.  careful of type mismatches.
            rgb_out *= self.colors[i] + [1.0]
            # normalize image
            rgb_out /= np.max(rgb_out)
            rgb_out = rgb_out.transpose((2, 1, 0))
            min_percent = .4 if i == self.nuc_index else .6
            lower_threshold, upper_threshold = get_thresholds(rgb_out, min_percent=min_percent)
            rgb_out = rgb_out.transpose((2, 1, 0))

            def superimpose(source_pixel, dest_pixel):
                pixel_weight = np.mean(source_pixel)
                if lower_threshold < pixel_weight < upper_threshold:
                    return source_pixel
                else:
                    return dest_pixel

            def alpha_blend(source_pixel, dest_pixel):
                pixel_weight = np.mean(source_pixel)
                if lower_threshold < pixel_weight < upper_threshold:
                    # this alpha value is based on the intensity of the pixel in the channel's original projection
                    alpha = projection[x, y]
                    # premultiplied alpha
                    return source_pixel + (1 - alpha) * dest_pixel
                else:
                    return dest_pixel

            layering_method = superimpose if self.layering_mode == "superimpose" else alpha_blend

            for x in range(rgb_out.shape[0]):
                for y in range(rgb_out.shape[1]):
                    # these slicing methods in C channel are getting the rgb data *only* and ignoring the alpha values
                    src_px = rgb_out[x, y, 0:3]
                    dest_px = layered_image[x, y, 0:3]
                    layered_image[x, y, 0:3] = layering_method(source_pixel=src_px, dest_pixel=dest_px)
                    # if mask_array has elements and the pixel is 0
                    if mask_array and mask_array[i][x,y] == 0.0:
                        layered_image[x, y, 3] = 0.0
                    else:
                        layered_image[x, y, 3] = 1.0

        return layered_image.transpose((2, 1, 0))

    def make_thumbnail(self, image, apply_cell_mask=False):
        """
        This method is the primary interface with the ThumbnailGenerator. It can be used many times with different images,
        in order to save the configuration that was specified at the beginning of the generator.

        :param image: single ZCYX image that is the source of the thumbnail
        :param apply_cell_mask: boolean value that designates whether the image is a fullfield or segmented cell
                                False -> fullfield, True -> segmented cell
        :return: a single CYX image, scaled down to the size designated in the constructor
        """

        # check to make sure there are 6 or more channels
        image = image.astype(np.float32)
        assert image.shape[1] >= 6
        assert max(self.memb_index, self.struct_index, self.nuc_index) <= image.shape[1] - 1

        im_size = np.array(image[:, 0].shape)
        assert len(im_size) == 3
        shape_out_rgb = self._get_output_shape(im_size)

        # ignore trans-light channel and seg channels
        num_noise_floor_bins = 256
        projection_array = []
        mask_array = []
        projection_type = self.projection_mode
        for i in self.channel_indices:
            # don't use max projections on the fullfield images... they get too messy
            if not apply_cell_mask:
                projection_type = 'slice'
            # subtract out the noise floor.
            thumb = subtract_noise_floor(image[:, i], bins=num_noise_floor_bins)
            thumb = np.asarray(thumb).astype('double')
            im_proj = create_projection(thumb, 0, projection_type, slice_index=int(thumb.shape[0] // 2), sections=self.proj_sections)
            if apply_cell_mask:
                mask_proj = create_projection(image[:, self.mask_channel_index], 0, method="slice", slice_index=int(image.shape[0] // 2))
                mask_array.append(mask_proj)
            projection_array.append(im_proj)

        layered_image = self._layer_projections(projection_array, mask_array)
        comp = resize_cyx_image(layered_image, shape_out_rgb)
        comp /= np.max(comp)
        comp[comp < 0] = 0
        # returns a CYX array for the png writer
        return comp
