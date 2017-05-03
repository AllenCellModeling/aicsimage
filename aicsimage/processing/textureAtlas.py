# author: Zach Crabtree zacharyc@alleninstitute.org

import math as m
import numpy as np
import os
import json
from scipy.ndimage.interpolation import zoom

from aicsimage.io.pngWriter import PngWriter
from aicsImage import AICSImage

# The design here is not great - there are lots of redundant variables passed from function to function
# The TextureAtlasGroup is helpful but doesn't do much besides encapsulate the save() function.
# There should be a smaller unit here which contains the necessary dimensions of tiles and atlases
# In the main call to get a TextureAtlasGroup, the code would go something like this:
#       atlas = TextureAtlas(image, pack_order[0])
#       atlas would contain metadata and actual png array
#       add TextureAtlas to group with metadata

class TextureAtlasGroup:
    def __init__(self, atlas_list, metadata, prefix):
        self.atlas_list = atlas_list
        self.prefix = prefix
        self.metadata = metadata

    def save(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        i = 0
        for atlas in self.atlas_list:
            full_path = os.path.join(output_dir, self.prefix + "_" + str(i) + ".png")
            with PngWriter(full_path, overwrite_file=True) as writer:
                writer.save(atlas)
            i += 1
        with open(os.path.join(output_dir, "atlas_meta.json"), 'w') as json_output:
            json.dump(self.metadata, json_output)

def _atlas_single_channel(im, channel, tile_width, tile_height, stack_height, atlas_width, atlas_height, rows, cols, scale):
    atlas = np.zeros((atlas_width, atlas_height))
    i = 0
    for row in range(rows):
        top_bound, bottom_bound = (tile_height * row), (tile_height * (row + 1))
        for col in range(cols):
            if i < stack_height:
                left_bound, right_bound = (tile_width * col), (tile_width * (col + 1))
                tile = zoom(im.get_image_data("XY", Z=i, C=channel), scale)
                atlas[left_bound:right_bound, top_bound:bottom_bound] = tile
                i += 1
    # transpose to YX for input into CYX arrays
    return atlas.transpose((1, 0))


def _calc_atlas_dimensions(tile_width, tile_height, stack_height, max_edge):
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
    atlas_edge = max(atlas_width, atlas_height)
    scale = float(max_edge) / atlas_edge
    atlas_width, atlas_height = int(atlas_width * scale), int(atlas_height * scale)
    return rows, cols, atlas_width, atlas_height, scale

# TODO get rid of the constant passing of tile_width, atlas_width, etc.
def generate_texture_atlas(im, prefix="atlas", max_edge=2048, pack_order=None):
    """
    Creates a TextureAtlasGroup object
    :param im: aicsImage object
    :param outpath: string containing directory path to save images in
    :param prefix: all atlases will be saved with this prefix and append _x for each atlas for the image
    :param max_edge: this designates the largest side in the texture atlas
    :param pack_order: a 2d list that contains what channel in the image should be saved to the RGBA values in the
                       final png. for example, a 7 channel image might be saved like [[0, 1, 2, 3], [4, 5], [6]]
                       where the first texture atlas will code channel 0 as r, channel 1 as g, and so on.
    :return: TextureAtlasGroup object
    """
    if not isinstance(im, AICSImage):
        raise ValueError("Texture atlases can only be generated with AICSImage objects!")
    if pack_order is None:
        # if no pack order is specified, pack 4 channels per png and move on
        channel_list = [c for c in range(im.shape[1])]
        pack_order = [channel_list[x:x+4] for x in xrange(0, len(channel_list), 4)]
    # this var generates the right suffix for each image
    atlas_list, image_meta_list = [], []
    tile_width, tile_height, stack_height = im.size_x, im.size_y, im.size_z
    rows, cols, atlas_width, atlas_height, scale = _calc_atlas_dimensions(tile_width, tile_height, stack_height, max_edge)
    tile_width, tile_height = int(tile_width * scale), int(tile_height * scale)
    png_count = 0
    for png in pack_order:
        if len(png) > 4:
            raise ValueError("An atlas with more than 4 channels ({}) cannot be created!".format(png))
        for channel in png:
            if channel > im.size_c:
                raise IndexError("A channel with value {} is out-of-bounds in the AICSImage object!".format(channel))

        # atlas is a CYX png
        atlas = np.ndarray((len(png), atlas_height, atlas_width))
        layer = 0
        for channel in png:
            atlas[layer] = _atlas_single_channel(im, channel,
                                                 tile_width, tile_height, stack_height,
                                                 atlas_width, atlas_height,
                                                 rows, cols, scale)
            layer += 1

        atlas_list.append(atlas)
        image_meta = {
            "name": prefix + "_" + str(png_count) + ".png",
            "channels": png
        }
        png_count += 1
        image_meta_list.append(image_meta)

    metadata = {
        "rows": rows,
        "cols": cols,
        "tiles": stack_height,
        "tile_width": tile_width,
        "tile_height": tile_height,
        "atlas_width": atlas_width,
        "atlas_height": atlas_height,
        "images": image_meta_list
    }

    return TextureAtlasGroup(atlas_list, metadata=metadata, prefix=prefix)






