# author: Zach Crabtree zacharyc@alleninstitute.org

import math as m
import numpy as np
import os
from aicsimage.io.pngWriter import PngWriter

from aicsImage import AICSImage
# class TextureAtlas:
#
#     def __init__(self, im, outpath, prefix, max_edge, pack_order):
#         self.image_stack = im
#         self.outpath = outpath
#         self.prefix = prefix
#         self.max_edge = max_edge
#         self.pack_order = pack_order

def _atlas_single_channel(im, channel, tile_width, tile_height, stack_height):
    # maintain aspect ratio of images
    # initialize atlas with one row of all slices
    atlas_width = tile_width * stack_height
    atlas_height = tile_height
    ratio = float(atlas_width) / float(atlas_height)
    # these next steps attempt to optimize the atlas into a square shape
    # TODO - there must be a way to do this with a single calculation
    for r in range(2, stack_height):
        new_rows = m.ceil(float(stack_height) / r)
        adjusted_width = int(tile_width * new_rows)
        adjusted_height = int(tile_height * r)
        new_ratio = float(max(adjusted_width, adjusted_height)) / float(min(adjusted_width, adjusted_height))
        if new_ratio < ratio:
            ratio = new_ratio
            atlas_width = adjusted_width
            atlas_height = adjusted_height
        else:
            # we've found the rows and columns that make this the most square image
            break

    cols = int(atlas_width // tile_width)
    rows = int(atlas_height // tile_height)
    atlas = np.zeros((atlas_width, atlas_height))
    i = 0
    for row in range(rows):
        top_bound, bottom_bound = (tile_height * row), (tile_height * (row + 1))
        for col in range(cols):
            if i < stack_height:
                left_bound, right_bound = (tile_width * col), (tile_width * (col + 1))
                atlas[left_bound:right_bound, top_bound:bottom_bound] = im.get_image_data("XY", Z=i, C=channel)
                i += 1

    return atlas

def generate_texture_atlas(im, outpath="text_atlases/", prefix="atlas", max_edge=2048, pack_order=None):
    """

    :param im: aicsImage object
    :param outpath: string containing directory path to save images in
    :param prefix: all atlases will be saved with this prefix and append _x for each atlas for the image
    :param max_edge: this designates the largest side in the texture atlas
    :param pack_order: a 2d list that contains what channel in the image should be saved to the RGBA values in the
                       final png. for example, a 7 channel image might be saved like [[0, 1, 2, 3], [4, 5], [6]]
                       where the first texture atlas will code channel 0 as r, channel 1 as g, and so on.
    :return:
    """
    if not isinstance(im, AICSImage):
        raise ValueError("Texture atlases can only be generated with AICSImage objects!")
    if pack_order is None:
        # if no pack order is specified, pack 4 channels per png and move on
        channel_list = [c for c in range(im.shape[1])]
        pack_order = [channel_list[x:x+4] for x in xrange(0, len(channel_list), 4)]
    png_count = 0
    for png in pack_order:
        if len(png) > 4:
            raise ValueError("An atlas with more than 4 channels ({}) cannot be created!".format(png))
        for channel in png:
            if channel > im.shape[1]:
                raise IndexError("A channel with value {} is out-of-bounds in the AICSImage object!".format(channel))
        stack_height, tile_height, tile_width = im.shape[2], im.shape[3], im.shape[4]
        layer_list = []
        for channel in png:
            xy_layer = _atlas_single_channel(im, channel, tile_width, tile_height, stack_height)
            layer_list.append(xy_layer)
        atlas_width, atlas_height = layer_list[0].shape[0], layer_list[0].shape[1]
        # atlas is a CYX png
        atlas = np.ndarray((len(png), atlas_height, atlas_width))
        i = 0
        for layer in layer_list:
            atlas[i] = layer.transpose(1, 0)
            i += 1
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        full_path = os.path.join(outpath, prefix + "_" + str(png_count) + ".png")
        with PngWriter(full_path, overwrite_file=True) as writer:
            writer.save(atlas)
        png_count += 1






