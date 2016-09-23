#!/usr/bin/env python

# author: Dan Toloudis danielt@alleninstitute.org

from aicsimagetools import *
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
# import scipy.ndimage
import sys
import time

z_axis_index = 0

def imresize(im, new_size, order=1):
    new_size = np.array(new_size).astype('double')
    old_size = np.array(im.shape).astype('double')

    zoom_size = np.divide(new_size, old_size)
    # precision?
    im_out = scipy.ndimage.interpolation.zoom(im, zoom_size)

    return im_out


def imdownsize(im, ratio, order=1):
    new_size = np.array(ratio).astype('double')
    zoom_size = 1/new_size

    im_out = scipy.ndimage.interpolation.zoom(im, zoom_size)

    return im_out


def mask_image(im, mask):
    im_masked = np.multiply(im, mask > 0)
    return im_masked


def matproj(im, dim, method='max'):
    if method == 'max':
        im = np.max(im, dim)
    elif method == 'mean':
        im = np.mean(im, dim)
    elif method == 'sum':
        im = np.sum(im, dim)

    return im


def im2projection(im_orig, method='max', cmap='jet', justz=False, rescaleinten=True, rescalechan=True):
    # todo:
    # 	if image input into im2projection is double, skip the indexing part
    # 	define a string as cmap or a n x 3 rgb matrix

    if type(im_orig) is list or type(im_orig) is tuple:
        istuple = True
    else:
        istuple = False

    if istuple:
        uimg = range(1, len(im_orig) + 1)
    else:
        uimg = np.unique(im_orig[:])
        uimg = uimg[uimg != 0]

    if isinstance(cmap, basestring):
        colors = plt.get_cmap(cmap)(np.linspace(0, 1, len(uimg)))
    else:
        colors = np.array(cmap)
        cshape = colors.shape

        assert cshape[0] == len(uimg)
        assert cshape[1] == 3

    if istuple:
        imsize = im_orig[0].shape
    else:
        imsize = im_orig.shape

    if len(imsize) == 2:
        imsize = np.hstack((1, imsize))
        im_orig = np.expand_dims(im_orig, 3)

    im_all = np.zeros(np.hstack((imsize[z_axis_index] + imsize[1], imsize[z_axis_index] + imsize[2], 3, len(uimg))))

    for i in range(0, len(uimg)):
        if istuple:
            im = im_orig[i]
        else:
            im = im_orig == uimg[i]

        im = np.asarray(im).astype('double')

        if justz:
            imsize[z_axis_index] = 0

        imz = matproj(im, z_axis_index, method)

        imx = []
        imy = []

        if not justz:

            imx = matproj(im, 1, method)
            imy = matproj(im, 2, method)

            if imsize[z_axis_index] == 1:
                imx = np.expand_dims(imx, 1)
                imy = np.expand_dims(imy, 1)

        im_tmp = np.zeros((imsize[z_axis_index] + imsize[1], imsize[z_axis_index] + imsize[2]))

        # imz is xXy
        im_tmp[0:imsize[1], imsize[0]:] = imz
        # imy is zXx
        im_tmp[0:imsize[1], 0:imsize[0]] = np.transpose(imy)
        # imx is zXy
        im_tmp[imsize[1]:, imsize[0]:] = imx

        im_tmp = np.expand_dims(im_tmp, 2)
        im_tmp = np.repeat(im_tmp, 3, 2)

        im_tmp[:, :, 0] *= colors[i, 0]
        im_tmp[:, :, 1] *= colors[i, 1]
        im_tmp[:, :, 2] *= colors[i, 2]

        if rescaleinten:
            im_tmp = im_tmp / np.max(im_tmp.flatten())

        im_all[:, :, :, i] = im_tmp

    im_out = np.sum(im_all, axis=3)

    if rescaleinten:
        im_out = im_out / np.max(im_out.flatten())

    return im_out

def make_rgb_proj(imxyz, axis, color, method='max', rescale_inten=True):
    imdbl = np.asarray(imxyz).astype('double')
    # do projection
    im_proj = matproj(imdbl, axis, method)

    # turn into RGB
    im_proj = np.expand_dims(im_proj, 2)
    im_proj = np.repeat(im_proj, 3, 2)

    # inject color.  careful of type mismatches.
    im_proj[:, :, 0] *= color[0]
    im_proj[:, :, 1] *= color[1]
    im_proj[:, :, 2] *= color[2]

    if rescale_inten:
        im_proj = im_proj / np.max(im_proj.flatten())

    return im_proj

def arrange(projz, projx, projy, sx, sy, sz, rescale_inten=True):
    # assume all images are shape [x,y,3]
    # do stuff and return big image
    shZ = projz.shape
    shX = projx.shape
    shY = projy.shape
    assert (len(shZ) == len(shY) == len(shX) == 3)

    im_all = np.zeros(np.hstack((sx+sz, sy+sz, 3)))
    # imz is xXy
    im_all[0:sx, sz:] = projz
    # imy is zXx (so transpose it)
    im_all[0:sx, 0:sz] = np.transpose(projy, (1,0,2))
    # imx is zXy
    im_all[sx:, sz:] = projx

    if rescale_inten:
        im_all = im_all / np.max(im_all.flatten())

    return im_all

# # max, sum, min, mean, inv_sum
# def generate_thumbnail(w,h, src_img, colors, slices, projection_axis, projection_type='max'):
#     shape = src_img.shape
#
#     make_rgb_proj(imxyz, axis, color, method='max', rescale_inten=True):
#
#     # do resizing last!
#
#     return img


def main():
    # parser = argparse.ArgumentParser(description='Interleave tiff files as channels in a single tiff. '
    #                                              'Example: python interleave.py --path /path/to/images/alphactinin/ '
    #                                              '--prefix img40_1')
    # parser.add_argument('--path', required=True, help='input path (directory only)')
    # parser.add_argument('--prefix', required=True, help='input file name prefix. Expects prefix_channelname.tif')
    # parser.add_argument('--outpath', default='./', help='output file path (directory only)')
    # args = parser.parse_args()


    reader0 = tifReader.TifReader('test/img40_1_dna.tif')
    reader1 = tifReader.TifReader('test/img40_1_memb.tif')
    reader2 = tifReader.TifReader('test/img40_1_struct.tif')
    reader3 = tifReader.TifReader('test/img40_1_seg_cell.tif')
    # reader4 = tifReader.TifReader('test/img40_1_seg_nuc.tif')

    # d = np.ndarray([reader0.size_z(), 5, reader0.size_y(), reader0.size_x()], dtype=reader0.dtype())
    # for i in range(reader0.size_z()):
    #     d[i, 0, :, :] = reader0.load_image(z=i)
    #     d[i, 1, :, :] = reader1.load_image(z=i)
    #     d[i, 2, :, :] = reader2.load_image(z=i)
    #     d[i, 3, :, :] = reader3.load_image(z=i)
    #     d[i, 4, :, :] = reader4.load_image(z=i)
    #
    # d2 = np.ndarray([reader0.size_y(), reader0.size_x(), 3])
    # d2[:,:,0] = d[reader0.size_z()/2, 0, :,:]
    # d2[:,:,1] = d[reader0.size_z()/2, 1, :,:]
    # d2[:,:,2] = d[reader0.size_z()/2, 2, :,:]
    # x0 = d2[:,:,0].max()
    # x1 = d2[:,:,1].max()
    # x2 = d2[:,:,2].max()
    # n0 = d2[:,:,0].min()
    # n1 = d2[:,:,1].min()
    # n2 = d2[:,:,2].min()
    # d2[:,:,0] -= n0
    # d2[:,:,1] -= n1
    # d2[:,:,2] -= n2
    # d2[:,:,0] *= 255.0/(x0-n0)
    # d2[:,:,1] *= 255.0/(x1-n1)
    # d2[:,:,2] *= 255.0/(x2-n2)
    #
    # pngwriter = pngWriter.PngWriter('test/o.png')
    # pngwriter.save(d2)



    ind = 0
    # dna, memb, struct, cellseg
    im1 = [reader0.load(), reader1.load(), reader2.load(), reader3.load()]

    imsize = np.array(im1[0].shape)
    assert len(imsize) == 3
    # 1/5 resizing
    # cut down the x and y slices to be closer to the z slices
    shape_out = np.hstack((imsize[0], imsize[1]/5, imsize[2]/5))

    print('Downsampling image1 with imresize')
    # apply the cell segmentation mask.  bye bye to data outside the cell
    im1 = [mask_image(im, im1[-1]) for im in im1]
    # resize AFTER masking but BEFORE projecting?
    im1 = [imresize(im, shape_out) for im in im1]

    t0 = time.clock()
    rgb0 = im2projection([im1[i] for i in [0, 2, 1]])
    t1 = time.clock()
    print('TIME_OLD : ' + str(t1-t0))
    print('Constructing image projection')
    plt.figure
    plt.imshow(rgb0)
    plt.show()


    t0 = time.clock()

    # get me 3 colors.
    # colors = plt.get_cmap('jet')(np.linspace(0, 1, 3))
    colors = [[0.0, 1.0, 1.0],[1.0, 0.0, 1.0],[1.0, 1.0, 0.0]]

    # xXy for Z projection
    combinedZ = np.zeros((shape_out[1], shape_out[2], 3))
    for i, im in enumerate([im1[i] for i in [0, 2, 1]]):
        rgbproj = make_rgb_proj(im, z_axis_index, colors[i])
        combinedZ += rgbproj
    # normalize to 0..max_intensity
    combinedZ = combinedZ / np.max(combinedZ.flatten())

    combinedX = np.zeros((shape_out[0], shape_out[2], 3))
    for i, im in enumerate([im1[i] for i in [0, 2, 1]]):
        rgbproj = make_rgb_proj(im, 1, colors[i])
        combinedX += rgbproj
    # normalize to 0..max_intensity
    combinedX = combinedX / np.max(combinedX.flatten())

    combinedY = np.zeros((shape_out[0], shape_out[1], 3))
    for i, im in enumerate([im1[i] for i in [0, 2, 1]]):
        rgbproj = make_rgb_proj(im, 2, colors[i])
        combinedY += rgbproj
    # normalize to 0..max_intensity
    combinedY = combinedY / np.max(combinedY.flatten())

    final = arrange(combinedZ, combinedX, combinedY, shape_out[1], shape_out[2], shape_out[0])
    t1 = time.clock()
    print('TIME NEW : ' + str(t1-t0))

    pngwriter = pngWriter.PngWriter('test/oComp.png')
    pngwriter.save(final)
    # pngwriter = pngWriter.PngWriter('test/oRGB0.png')
    # pngwriter.save(rgb0)

    rgb1 = im2projection([im1[i] for i in [0, 2]], cmap=np.array([[0, 0, 1], [0, 1, 0]]))
    print('Constructing image projection')
    plt.figure
    # plt.imshow(im2projection([im1[i] for i in [0,2]], cmap=np.array([[0,0,1],[ 0,1,0]])))
    plt.subplot(1, 2, 1)
    plt.imshow(rgb1)

    rgb2 = im2projection([im1[i] for i in [1]], cmap=np.array([[1, 0, 0]]))
    plt.subplot(1, 2, 2)
    plt.imshow(rgb2)
    plt.show()


if __name__ == "__main__":
    print sys.argv
    main()
    sys.exit(0)
