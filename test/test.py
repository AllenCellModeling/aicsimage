#!/usr/bin/env python

# author: Dan Toloudis danielt@alleninstitute.org

import argparse
# import bioformats
# from tifftools import bioformatutils2
from tifftools import omeTifReader
from tifftools import tifReader
from tifftools import omeTifWriter
from tifftools import pngWriter
from tifftools import omexml
# import javabridge
import numpy as np
# import os
# import sys


def mymain():
    #bioformatutils2.initBioformats()

    # reader = omeTifReader.OmeTifReader('test/img40_1_dna.tif')
    # meta = reader.get_metadata()


    reader0 = tifReader.TifReader('test/img40_1_dna.tif')
    reader1 = tifReader.TifReader('test/img40_1_memb.tif')
    reader2 = tifReader.TifReader('test/img40_1_struct.tif')
    reader3 = tifReader.TifReader('test/img40_1_seg_cell.tif')
    reader4 = tifReader.TifReader('test/img40_1_seg_nuc.tif')

    d = np.ndarray([reader0.size_z(), 5, reader0.size_y(), reader0.size_x()], dtype=reader0.dtype())
    for i in range(reader0.size_z()):
        d[i, 0, :, :] = reader0.load_image(z=i)
        d[i, 1, :, :] = reader1.load_image(z=i)
        d[i, 2, :, :] = reader2.load_image(z=i)
        d[i, 3, :, :] = reader3.load_image(z=i)
        d[i, 4, :, :] = reader4.load_image(z=i)

    writer = omeTifWriter.OmeTifWriter('test/o.ome.tif')
    writer.save(d)
    writer.close()

    d2 = np.ndarray([reader0.size_y(), reader0.size_x(), 3])
    d2[:,:,0] = d[reader0.size_z()/2, 0, :,:]
    d2[:,:,1] = d[reader0.size_z()/2, 1, :,:]
    d2[:,:,2] = d[reader0.size_z()/2, 2, :,:]
    x0 = d2[:,:,0].max()
    x1 = d2[:,:,1].max()
    x2 = d2[:,:,2].max()
    n0 = d2[:,:,0].min()
    n1 = d2[:,:,1].min()
    n2 = d2[:,:,2].min()
    d2[:,:,0] -= n0
    d2[:,:,1] -= n1
    d2[:,:,2] -= n2
    d2[:,:,0] *= 255.0/(x0-n0)
    d2[:,:,1] *= 255.0/(x1-n1)
    d2[:,:,2] *= 255.0/(x2-n2)

    pngwriter = pngWriter.PngWriter('test/o.png')
    pngwriter.save(d2)

    omereader = omeTifReader.OmeTifReader('test/img40_1.ome.tif')
    sz = omereader.size_z()

    bits = np.empty([40,3,100,100], dtype=np.uint16)

    writer = bioformatutils2.BioformatsWriter("o.ome.tif")
    writer.saveXYCZ(bits, dtype='uint16')

    #
    # reader = bioformatutils.open("o.ome.tif")
    # meta = bioformatutils.loadMetadata(reader)
    # x = meta.dumpXML()
    # cc = meta.getPixelsSizeC(0)
    # ct = meta.getPixelsSizeT(0)
    # cz = meta.getPixelsSizeZ(0)
    # bioformatutils.close(reader)

    reader = bioformatutils2.BioformatsReader("o.ome.tif")
    cc = reader.metadata.PixelsSizeC(0)
    ct = reader.metadata.PixelsSizeT(0)
    cz = reader.metadata.PixelsSizeZ(0)

    im = reader.get_frame_2D(c=1, z=4)

    bioformatutils2.shutdownModule()

# bioformatutils2.jpype.setupGuiEnvironment(mymain)
mymain()


