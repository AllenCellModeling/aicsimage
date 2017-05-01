# author: Zach Crabtree zacharyc@alleninstitute.org

import unittest

from aicsimage.processing.aicsImage import AICSImage


class TextureAtlasTestGroup(unittest.TestCase):

    def test_Sizing(self):
        # arrange
        image = AICSImage("img/img40_1.ome.tif")
        max_edge = 2048
        # act
        atlas = generate_texture_atlas(im=image, outpath="img/atlas/",
                                       prefix="atlas", max_edge=max_edge)
        atlas_maxedge = max(atlas.shape[0], atlas.shape[1])
        # assert
        self.assertEqual(atlas_maxedge, max_edge)

    def test_pickChannels(self):
        # arrange
        image = AICSImage("img/img40_1.ome.tif")
        packing_list = [[0], [1, 2], [3, 4], [5, 6]]
        # act
        atlas = generate_texture_atlas(image, packing=packing_list)
        # returns as dict
        metadata = atlas.get_metadata()
        # returns list of dicts
        image_dicts = metadata["images"]
        output_packed = [image.channels for image in image_dicts]
        # assert
        self.assertEqual(packing_list, output_packed)

    def test_metadata(self):
        # arrange
        image = AICSImage("img/img40_1.ome.tif")
        packing_list = [[0], [1, 2], [3, 4], [5, 6]]
        output_dir = "img/atlas"
        prefix = "atlas"
        # act
        atlas = generate_texture_atlas(image, outpath=output_dir, fileprefix=prefix,
                                       packing=packing_list)
        # assert
        metadata = atlas.get_metadata()
        self.assertTrue(all(key in metadata for key in ("rows", "cols", "width", "height", "images")))



