#!/usr/bin/env python

# author: Dan Toloudis danielt@alleninstitute.org

# import argparse
from aicsimagetools import omeTifReader
from aicsimagetools import tifReader
from aicsimagetools import omeTifWriter
from aicsimagetools import pngWriter
from aicsimagetools import cziReader
# from aicsimagetools import omexml
import numpy as np
# import os
# import sys


def main():
    # czr = cziReader.CziReader('test/20160705_I01_001.czi')
    # czdata = czr.load()
    #
    #
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
    #
    # writer = omeTifWriter.OmeTifWriter('test/o.ome.tif')
    # writer.save(d)
    # writer.close()

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


main()


