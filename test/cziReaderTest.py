#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import pngWriter
from aicsimagetools import cziReader
import numpy as np
from transformationTest import transform


def main():

    czireader = cziReader.CziReader('T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi')
    czi_image = np.ndarray([czireader.size_z(), czireader.size_c(), czireader.size_y(), czireader.size_x()],
                           dtype=czireader.dtype())
    czi_loaded = czireader.load()

    for i in range(czireader.size_z()):
        for j in range(czireader.size_c()):
            if len(czireader.czi.shape) == 7:
                czi_image[i, j, :, :] = czi_loaded[0, i, j, :, :]
            else:
                czi_image[i, j, :, :] = czi_loaded[i, j, :, :]

    czi_image_2 = np.ndarray([czireader.size_x(), czireader.size_y(), 1], dtype=czireader.dtype())

    czi_image_2[:, :, 0] = czireader.load_image(z=1, c=1, t=1)

    pngwriter = pngWriter.PngWriter('czitest.png')
    pngwriter.save(transform(czi_image))
    pngwriter.close()

    # output a single slice to test the load_image function
    pngwriter = pngWriter.PngWriter('czitest2.png')
    pngwriter.save(czi_image_2)
    pngwriter.close()

main()
