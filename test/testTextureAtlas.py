# author: Zach Crabtree zacharyc@alleninstitute.org

import unittest

from aicsimage.processing.aicsImage import AICSImage
from aicsimage.processing.textureAtlas import generate_texture_atlas


class TextureAtlasTestGroup(unittest.TestCase):

    def test_Save(self):
        image = AICSImage("img/img40_1.ome.tif")
        atlas = generate_texture_atlas(im=image, pack_order=[[0, 1, 2], [3], [4]], prefix="test_Sizing", max_edge=1024)
        atlas.save("img/atlas_max")

    def test_Sizing(self):
        # arrange
        image = AICSImage("img/img40_1.ome.tif")
        max_edge = 2048
        # act
        atlas = generate_texture_atlas(im=image,
                                       prefix="test_Sizing", max_edge=max_edge,
                                       pack_order=[[3, 2, 1, 0], [4]])
        atlas_maxedge = max(atlas.dims.atlas_width, atlas.dims.atlas_height)
        # assert
        self.assertTrue(atlas_maxedge <= max_edge)

    def test_pickChannels(self):
        # arrange
        image = AICSImage("img/img40_1.ome.tif")
        packing_list = [[0], [1, 2], [3, 4]]
        # act
        atlas = generate_texture_atlas(image, prefix="test_pickChannels", pack_order=packing_list)
        # returns as dict
        # metadata = atlas.get_metadata()
        # returns list of dicts
        image_dicts = atlas.atlas_list
        output_packed = [image.metadata['channels'] for image in image_dicts]
        # assert
        self.assertEqual(packing_list, output_packed)

    def test_metadata(self):
        # arrange
        image = AICSImage("img/img40_1.ome.tif")
        packing_list = [[0], [1, 2], [3, 4]]
        output_dir = "img/atlas/"
        prefix = "atlas"
        # act
        atlas = generate_texture_atlas(image, prefix=prefix,
                                       pack_order=packing_list)
        # assert
        metadata = atlas.get_metadata()
        self.assertTrue(all(key in metadata for key in ("tile_width", "tile_height", "width", "height", "channels", "channel_names", "tiles", "rows", "cols", "atlas_width", "atlas_height", "images")))
        self.assertTrue(len(metadata["channel_names"]) == metadata["channels"])


