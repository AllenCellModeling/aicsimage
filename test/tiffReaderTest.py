#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import tifReader
from aicsimagetools import pngWriter
import numpy as np
from transformationTest import transform


def main():
    reader0 = tifReader.TifReader('img40_1_dna.tif')
    reader1 = tifReader.TifReader('img40_1_memb.tif')
    reader2 = tifReader.TifReader('img40_1_struct.tif')
    reader3 = tifReader.TifReader('img40_1_seg_cell.tif')
    reader4 = tifReader.TifReader('img40_1_seg_nuc.tif')

    reader_array = [reader0, reader1, reader2, reader3, reader4]

    d = np.ndarray([reader_array[0].size_z(), 5, reader_array[0].size_y(), reader_array[0].size_x()],
                   dtype=reader_array[0].dtype())
    for i in range(reader_array[0].size_z()):
        d[i, 0, :, :] = reader_array[0].load_image(z=i)
        d[i, 1, :, :] = reader_array[1].load_image(z=i)
        d[i, 2, :, :] = reader_array[2].load_image(z=i)
        d[i, 3, :, :] = reader_array[3].load_image(z=i)
        d[i, 4, :, :] = reader_array[4].load_image(z=i)

    pngwriter = pngWriter.PngWriter('tiftest.png')
    pngwriter.save(transform(d))
    pngwriter.close()

main()