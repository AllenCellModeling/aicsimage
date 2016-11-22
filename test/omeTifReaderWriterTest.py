#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

from aicsimagetools import omeTifReader
from aicsimagetools import pngWriter
import numpy as np
from transformationTest import transform


def main():
    omereader = omeTifReader.OmeTifReader('img40_1.ome.tif')

    initial_image = np.ndarray([omereader.size_z(), omereader.size_c(), omereader.size_y(), omereader.size_x()],
                               dtype=omereader.dtype())
    for i in range(omereader.size_z()):
        for j in range(omereader.size_c()):
            initial_image[i, j, :, :] = omereader.load_image(z=i, c=j)

    omereader.load()

    transformed_image = transform(initial_image)

    pngwriter = pngWriter.PngWriter('ometiftest.png')
    pngwriter.save(transformed_image)
    pngwriter.close()

main()
