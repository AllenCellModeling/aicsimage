#!/usr/bin/env python

# author: Dan Toloudis danielt@alleninstitute.org

from aicsimagetools import *
import argparse
import numpy as np
import os
import sys


def main():
    # python interleave.py --path /Volumes/aics/software_it/danielt/images/AICS/alphactinin/ --prefix img40_1
    parser = argparse.ArgumentParser(description='Interleave tiff files as channels in a single tiff. '
                                     'Example: python interleave.py --path /path/to/images/alphactinin/ '
                                     '--prefix img40_1')
    parser.add_argument('--path', required=True, help='input path (directory only)')
    parser.add_argument('--prefix', required=True, help='input file name prefix. Expects prefix_channelname.tif')
    parser.add_argument('--outpath', default='./', help='output file path (directory only)')
    # parser.add_argument('--prefix', nargs=1, help='input file name prefix')
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

    try:
        readers = []

        assert len(image_paths_in) == len(channels)
        # open each file that we are going to interleave
        for i, channelName in enumerate(channels):
            image_path_in = image_paths_in.get(channelName)
            if image_path_in is None:
                raise Exception('Missing channel file for channel ' + channelName)

            readers.append(TifReader(image_path_in))

        assert len(readers) == len(channels)

        # do the interleaving, reading one slice at a time from each of the single channel tifs
        d = np.ndarray([readers[0].size_z(), 5, readers[0].size_y(), readers[0].size_x()], dtype=readers[0].dtype())
        for i in range(readers[0].size_z()):
            for j in range(len(readers)):
                d[i, j, :, :] = readers[j].load_image(z=i)
            # d[i, 0, :, :] = readers[0].load_image(z=i)
            # d[i, 1, :, :] = readers[1].load_image(z=i)
            # d[i, 2, :, :] = readers[2].load_image(z=i)
            # d[i, 3, :, :] = readers[3].load_image(z=i)
            # d[i, 4, :, :] = readers[4].load_image(z=i)

        try:
            os.remove(image_out)
            print('previous output file deleted')
        except:
            print('no output file to delete')

        writer = omeTifWriter.OmeTifWriter(image_out)
        writer.save(d, channel_names=[x.upper() for x in channels])
        writer.close()
        print('Completed ' + image_out)

    except Exception as inst:
        print(inst)

if __name__ == "__main__":
    print sys.argv
    main()
    sys.exit(0)
