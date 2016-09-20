#!/usr/bin/env python

# author: Dan Toloudis danielt@alleninstitute.org

import argparse
import bioformats
import bioformatutils
import javabridge
import numpy as np
import os
import sys

def main(argin):
    # python interleave.py --path /Volumes/aics/software_it/danielt/images/AICS/alphactinin/ --prefix img40_1
    parser = argparse.ArgumentParser(description='Interleave tiff files as channels in a single tiff.')
    parser.add_argument('--path', required=True, help='input path (directory only)')
    parser.add_argument('--prefix', required=True, help='input file name prefix. Expects prefix_channelname.tif')
    parser.add_argument('--outpath', default='./', help='output file path (directory only)')
    #parser.add_argument('--prefix', nargs=1, help='input file name prefix')
    args = parser.parse_args()

    inpath = args.path
    inseries = args.prefix
    channels = ['dna', 'memb', 'struct', 'seg_nuc', 'seg_cell']
    tifext = '.tif'

    # dictionary of channelname:fullpath
    image_paths_in = {}
    for i in channels:
        fullpath = os.path.join(inpath, inseries + '_' + i + tifext)
        if os.path.isfile(fullpath):
            image_paths_in[i] = fullpath

    image_out = os.path.join(args.outpath, inseries + '.ome' + tifext)

    bioformatutils.initBioformats()

    try:

        zsize = 0
        zsizelast = 0
        for i,channelName in enumerate(channels):
            image_path_in = image_paths_in.get(channelName)
            if image_path_in == None:
                raise Exception('Missing channel file for channel ' + channelName)

            im_reader = bioformats.ImageReader(image_path_in)
            metadata = bioformats.metadatatools.MetadataRetrieve(im_reader.metadata)

            size_x = im_reader.rdr.getSizeX()
            size_y = im_reader.rdr.getSizeY()

            # i am expecting input files with no more than 1 channel
            size_c = im_reader.rdr.getSizeC()
            assert(size_c < 2)

            # i am expecting input files with (z=1 and t>1) or (t=1 and z>1)
            # should assert that this zsize is the same for all files coming in.
            size_z = im_reader.rdr.getSizeZ()
            size_t = im_reader.rdr.getSizeT()
            assert ((size_t==1 and size_z>1) or (size_t>1 and size_z==1)), 'Expected one of z or t count to be 1, and the other to be greater'
            # either way i'm turning it into z.
            zsize = max(size_t, size_z)

            # first time through, init my big giant array
            if i == 0:
                xycz = np.empty([zsize, len(channels), size_y, size_x])
            else:
                assert (zsize == zsizelast), 'different number of slices in different channels!'

            zsizelast = zsize

            # read slices into the array
            print('Parsing image ' + image_path_in)
            parse_image_path(im_reader, i, xycz)

        save(image_out, xycz, channels)
        print('Completed ' + image_out)


    except Exception as inst:
        print(inst)

    bioformatutils.shutDownBioformats()

def parse_image_path(im_reader, channelIndex, xycz):
    # parses out a image_path into individual tiff slices, and returns a table that captures all the information

    # import bioformats.formatwriter as writer

    size_c = im_reader.rdr.getSizeC()
    size_t = im_reader.rdr.getSizeT()
    size_z = im_reader.rdr.getSizeZ()
    size_s = im_reader.rdr.getSeriesCount()

    assert(size_c == 1)
    assert(size_s == 1)

    s_ind = 0
    for z_ind in range(0, size_z):
        for t_ind in range(0, size_t):
            for c_ind in range(0, size_c):
                image = im_reader.read(c=c_ind, z=z_ind, t=t_ind, series=s_ind, index=None, rescale=False, wants_max_intensity=False, channel_names=None)
                xycz[max(z_ind, t_ind), channelIndex] = image.astype(np.uint8)

def save(image_out, xycz, channel_names):
    try:
        os.remove(image_out)
        print('previous output file deleted')
    except:
        print('no output file to delete')

    bioformatutils.saveXYCZ(xycz, image_out, channel_names=[x.upper() for x in channel_names])

if __name__ == "__main__":
    print sys.argv
    main(sys.argv)
    # import threading
    # threading.enumerate()
    sys.exit(0)
