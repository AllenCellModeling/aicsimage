# author: Zach Crabtree zacharyc@alleninstitute.org

import math as m
import numpy as np
import os
import json
from scipy.ndimage.interpolation import zoom

from aicsimage.io.pngWriter import PngWriter
from aicsImage import AICSImage

class TextureAtlas:
    def __init__(self, aics_image, filename, pack_order, max_edge):
        self.max_edge = max_edge

        if not isinstance(aics_image, AICSImage):
            raise ValueError("Texture atlases can only be generated with AICSImage objects!")
        self.aics_image = aics_image

        if len(pack_order) > 4:
            raise ValueError("An atlas with more than 4 channels ({}) cannot be created!".format(pack_order))
        if any(channel > self.aics_image.size_c for channel in pack_order):
            raise IndexError("A channel specified in the ordering {} is out-of-bounds in the AICSImage object!".format(pack_order))

        self.pack_order = pack_order
        self.metadata = {
            "name": filename,
            "channels": self.pack_order
        }
        self.stack_height = self.aics_image.size_z
        self.tile_width, self.tile_height, self.rows, self.cols, self.atlas_width, self.atlas_height = self._calc_atlas_dimensions()
        self.atlas = self.generate_atlas()

    def _calc_atlas_dimensions(self):
        tile_width, tile_height, stack_height = self.aics_image.size_x, self.aics_image.size_y, self.aics_image.size_z
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

        if self.max_edge < atlas_width or self.max_edge < atlas_height:
            tile_width = m.floor(self.max_edge/cols)
            tile_height = m.floor(self.max_edge/rows)
            atlas_width = tile_width * cols
            atlas_height = tile_height * rows

        return int(tile_width), int(tile_height), int(rows), int(cols), int(atlas_width), int(atlas_height)

    def generate_atlas(self):
        atlas = np.zeros((len(self.pack_order), self.atlas_height, self.atlas_width))
        layer = 0
        for channel in self.pack_order:
            atlas[layer] = self._atlas_single_channel(channel)
            layer += 1
        return atlas

    def _atlas_single_channel(self, channel):
        scale = (float(self.tile_width) / float(self.aics_image.size_x), float(self.tile_height) / float(self.aics_image.size_y))

        chandata = self.aics_image.get_image_data("XYZ", C=channel)
        # renormalize
        chandata = chandata.astype(np.float32)
        chandata *= 255.0/chandata.max()

        atlas = np.zeros((self.atlas_width, self.atlas_height))
        i = 0
        for row in range(self.rows):
            top_bound, bottom_bound = (self.tile_height * row), (self.tile_height * (row + 1))
            for col in range(self.cols):
                if i < self.aics_image.size_z:
                    left_bound, right_bound = (self.tile_width * col), (self.tile_width * (col + 1))
                    # TODO fix scaling being off by one pixel due to rounding
                    tile = zoom(chandata[:,:,i], scale)
                    atlas[left_bound:right_bound, top_bound:bottom_bound] = tile.astype(np.uint8)
                    i += 1
        # transpose to YX for input into CYX arrays
        return atlas.transpose((1, 0))


class TextureAtlasGroup:
    def __init__(self, atlas_list=None, prefix="texture_atlas"):
        self.atlas_list = atlas_list
        self.prefix = prefix
        self.metadata = self._create_metadata()

    def _create_metadata(self):
        # if there are atlases in atlas list
        if self.atlas_list is not None:
            # all atlases in atlas_list will contain the same data necessary for this metadata
            atlas_template = self.atlas_list[0]
            metadata = {
                "width": atlas_template.aics_image.size_x,
                "height": atlas_template.aics_image.size_y,
                "channels": atlas_template.aics_image.size_c,
                "channel_names": ['CH_'+str(i) for i in range(atlas_template.aics_image.size_c)],
                "rows": atlas_template.rows,
                "cols": atlas_template.cols,
                "tiles": atlas_template.stack_height,
                "tile_width": atlas_template.tile_width,
                "tile_height": atlas_template.tile_height,
                "atlas_width": atlas_template.atlas_width,
                "atlas_height": atlas_template.atlas_height
            }
            image_list = []
            for atlas in self.atlas_list:
                image_list.append(atlas.metadata)
            metadata["images"] = image_list
        else:
            # if there are no atlases in the group, then metadata shouldn't contain anything
            metadata = None
        return metadata

    def _is_valid_atlas(self, atlas):
        if self.atlas_list is not None:
            element_list = ["rows", "cols", "tiles", "tile_width", "tile_height", "atlas_width", "atlas_height"]
            atlas_elements = [atlas.rows, atlas.cols, atlas.stack_height, atlas.tile_width, atlas.tile_height, atlas.atlas_width, atlas.atlas_height]
            matching = zip(element_list, atlas_elements)
            for key, atlas_val in matching:
                if self.metadata[key] != atlas_val:
                    return False
            return True
        else:
            # if there are no atlases in the group, the first atlas will determine validity of others
            return True


    def append(self, atlas):
        if not isinstance(atlas, TextureAtlas):
            raise ValueError("TextureAtlasGroup can only append TextureAtlas objects!")
        if self._is_valid_atlas(atlas):
            if self.atlas_list:
                self.atlas_list.append(atlas)
            else:
                self.atlas_list = [atlas]
            if self.metadata is None:
                self.metadata = self._create_metadata()
            else:
                self.metadata["images"].append(atlas.metadata)
        else:
            raise ValueError("Attempted to add atlas that doesn't match the rest of atlasGroup")

    def save(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        i = 0
        for atlas in self.atlas_list:
            full_path = os.path.join(output_dir, self.prefix + "_" + str(i) + ".png")
            with PngWriter(full_path, overwrite_file=True) as writer:
                writer.save(atlas.atlas)
            i += 1
        with open(os.path.join(output_dir, self.prefix + "_atlas.json"), 'w') as json_output:
            json.dump(self.metadata, json_output)

def generate_texture_atlas(im, prefix="texture_atlas", max_edge=2048, pack_order=None):
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
    max_channels_per_png = 3
    if pack_order is None:
        # if no pack order is specified, pack 4 channels per png and move on
        channel_list = [c for c in range(im.shape[1])]
        pack_order = [channel_list[x:x+max_channels_per_png] for x in xrange(0, len(channel_list), max_channels_per_png)]
    atlas_group = TextureAtlasGroup(prefix=prefix)
    png_count = 0
    for png in pack_order:
        file_path = prefix + "_" + str(png_count) + ".png"
        atlas = TextureAtlas(im, filename=file_path, pack_order=png, max_edge=max_edge)
        atlas_group.append(atlas)
        png_count += 1

    return atlas_group






