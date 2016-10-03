#!/usr/bin/env python

# author: Dan Toloudis danielt@alleninstitute.org

from aicsimagetools import *
import argparse
import numpy as np
import os
import scipy
import sys

z_axis_index = 0


def imresize(im, new_size):
    new_size = np.array(new_size).astype('double')
    old_size = np.array(im.shape).astype('double')

    zoom_size = np.divide(new_size, old_size)
    # precision?
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


def make_rgb_proj(imxyz, axis, color, method='max', rescale_inten=False):
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
    im_all[0:sx, 0:sz] = np.transpose(projy, (1, 0, 2))
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
    # python interleave.py --path /Volumes/aics/software_it/danielt/images/AICS/alphactinin/ --prefix img40_1
    parser = argparse.ArgumentParser(description='Generate thumbnail from a set of cell images. '
                                     'Example: python thumbnail.py --path /path/to/images/alphactinin/ '
                                     '--prefix img40_1')
    parser.add_argument('--path', required=True, help='input path (directory only)')
    parser.add_argument('--prefix', required=True, help='input file name prefix. Expects prefix_channelname.tif')
    parser.add_argument('--size', default=128, type=int, help='maximum edge size of image')
    parser.add_argument('--outpath', default='./', help='output file path (directory only)')
    # parser.add_argument('--prefix', nargs=1, help='input file name prefix')
    args = parser.parse_args()

    inpath = args.path
    inseries = args.prefix
    channels = ['dna', 'memb', 'struct', 'seg_cell']
    tifext = '.tif'

    # load all images in at once(?)
    im1 = []
    for i, suffix in enumerate(channels):
        fullpath = os.path.join(inpath, inseries + '_' + suffix + tifext)
        if os.path.isfile(fullpath):
            reader = tifReader.TifReader(fullpath)
            im1.append(reader.load())
        else:
            raise 'Bad file path ' + fullpath

    image_out = os.path.join(args.outpath, inseries + '.png')

    # see http://www.somersault1824.com/tips-for-designing-scientific-figures-for-color-blind-readers/
    # or http://mkweb.bcgsc.ca/biovis2012/
    colors = [
        [0.0/255.0, 109.0/255.0, 219.0/255.0],
        [36.0/255.0, 255.0/255.0, 36.0/255.0],
        [255.0/255.0, 109.0/255.0, 182.0/255.0],
        [1.0, 1.0, 0.0]
    ]

    # assume all images have same shape!!!
    imsize = np.array(im1[0].shape)
    assert len(imsize) == 3

    # size down to this edge size, maintaining aspect ratio.
    max_edge = args.size
    # keep same number of z slices.
    shape_out = np.hstack((imsize[0],
                           max_edge if imsize[1] > imsize[2] else max_edge*imsize[1]/imsize[2],
                           max_edge if imsize[1] < imsize[2] else max_edge*imsize[2]/imsize[1]
                           ))
    shape_out_rgb = (shape_out[1], shape_out[2], 3)

    # apply the cell segmentation mask.  bye bye to data outside the cell
    im1 = [mask_image(im, im1[-1]) for im in im1]

    num_noise_floor_bins = 16
    comp = np.zeros(shape_out_rgb)
    for i in range(3):
        # try to subtract out the noise floor.
        # range is chosen to ignore zeros due to masking.  alternative is to pass mask image as weights=im1[-1]
        hi, bin_edges = np.histogram(im1[i], bins=num_noise_floor_bins, range=(max(1, im1[i].min()), im1[i].max()))
        # hi, bin_edges = np.histogram(im1[0], bins=16, weights=im1[-1])
        # index of tallest peak in histogram
        peakind = np.argmax(hi)
        # subtract this out
        thumb = im1[i].astype(np.float32)
        thumb -= bin_edges[peakind]
        # don't go negative
        thumb[thumb < 0] = 0
        # renormalize
        thumb /= thumb.max()

        # resize before projection?
        # thumb = imresize(thumb, shape_out)
        rgbproj = make_rgb_proj(thumb, z_axis_index, colors[i])
        rgbproj = imresize(rgbproj, shape_out_rgb)
        comp += rgbproj
        # pngwriter = pngWriter.PngWriter('test/oThumb'+str(i)+'.png')
        # pngwriter.save(rgbproj)
    # renormalize
    # comp /= comp.max()
    pngwriter = pngWriter.PngWriter(image_out)
    pngwriter.save(comp)

if __name__ == "__main__":
    print sys.argv
    main()
    sys.exit(0)
