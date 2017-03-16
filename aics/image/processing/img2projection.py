# Author: Evan Wiederspan

#from aicsimagetools import *
import numpy as np
import matplotlib.pyplot as pplot


def matproj(im, dim, method='max', slice_index=0):
    if method == 'max':
        im = np.max(im, dim)
    elif method == 'mean':
        im = np.mean(im, dim)
    elif method == 'sum':
        im = np.sum(im, dim)
    elif method == 'slice':
        im = im[slice_index, :, :]
    else:
        raise ValueError
    return im


def im2projection(im1, proj_all=False, proj_method='max', colors=lambda i: [1, 1, 1], global_adjust=False, local_adjust=False):
    # im: either a 4d numpy array as CZYX, list of 3d ZYX np arrays, or list of 2d YX np arrays
    # method, str. 'mean', 'sum', 'max', or 'slice'. max by default
    # proj_all, true gives all 3 projections, false just gives xy. false by default
    # global_adjust, boolean. If true, will scale image as a whole to ensure that the max value is 255. False by default
    # local_adjust, boolean. If true, will scale each color channel independently to ensure that the max value is 255. False by default

    # TODO: turn this into one-liner with np.cat?
    # turn list of 2d or 3d arrays into single 4d array if needed
    try:
        if type(im1) == type([]):
            # if only YX, add a single Z dimen
            if im1[0].ndim == 2:
                im1 = list(map(lambda a: np.expand_dims(a,axis=0), im1))
            elif im1[0].ndim != 3:
                raise ValueError("im1 must be a list of 2d or 3d arrays")
            # combine list into 4d array
            im = np.stack(im1)
        else:
            if im1.ndim != 4:
                raise ValueError("Invalid dimensions for im1")
            im = im1

    except (AttributeError, IndexError):
        # its not a list of np arrays
        raise ValueError("im1 must be either a 4d numpy array or a list of numpy arrays")

    # color processing code
    if isinstance(colors, str):
        # pass it in to matplotlib
        try:
            colors = pplot.get_cmap(colors)(np.linspace(0, 1, im.shape[0]))
        except ValueError:
            # thrown when string is not valid function
            raise ValueError("Invalid cmap string")
    elif callable(colors):
        # if its a function
        try:
            colors = [colors(i) for i in range(im.shape[0])]
        except:
            raise ValueError("Invalid color function")

    # else, were assuming it's a list
    # scale colors down to 0-1 range if they're bigger than 1
    if any(v > 1 for v in np.array(colors).flatten()):
        colors = [[v / 255 for v in c] for c in colors]

    # create final image
    if not proj_all:
        img_final = np.zeros((3, im.shape[2], im.shape[3]))
    else:
        #                                 y + z,                     x + z
        img_final = np.zeros((3, im.shape[2] + im.shape[1], im.shape[3] + im.shape[1]))

    img_piece = np.empty(img_final.shape)
    # loop through all channels
    for i, img_c in enumerate(im):
        try:
            proj_z = matproj(img_c, 0, proj_method, im.shape[0] // 2)
            if proj_all:
                proj_y, proj_x = (matproj(img_c, axis, proj_method, im.shape[axis] // 2) for axis in range(1, 3))
                # flipping to get them facing the right way
                proj_x = np.fliplr(np.transpose(proj_x, (1, 0)))
                proj_y = np.flipud(proj_y)
                #img_piece = arrange(proj_z, proj_y, proj_x, proj_z.shape[1], proj_z.shape[0], proj_y.shape[0])
                sx, sy, sz = proj_z.shape[1], proj_z.shape[0], proj_y.shape[0]
                img_piece[:, :sy, :sz] = proj_x
                img_piece[:, :sy, sz:] = proj_z
                img_piece[:, sy:, sz:] = proj_y
            else:
                img_piece[:] = proj_z
        except ValueError:
            raise ValueError("Invalid projection function")

        for c in range(3):
            img_piece[c] *= colors[i][c]

        # local contrast adjustment, minus the min, divide the max
        if local_adjust:
            img_piece -= np.min(img_piece)
            img_piece /= np.max(img_piece)
        img_final += img_piece

    # color range adjustment, ensure that max value is 255
    if global_adjust:
        # scale color channels independently
        for c in range(3):
            max_val = np.max(img_final[c].flatten())
            if max_val > 0:
                img_final[c] *= (255 / max_val)

    return img_final


# def run(in_files):
#     img = [omeTifReader.OmeTifReader(f).load()[0] for f in in_files]
#     out = im2projection(img, proj_all=True, proj_method='max', colors='jet', local_adjust=True)
#     with pngWriter.PngWriter('5-channel-global-contrast.png', overwrite_file=True) as w:
#         w.save(out)
# run(['../20160708_I01_001_1.ome.tif_memb.tif', '../20160708_I01_001_1.ome.tif_nuc.tif', '../20160708_I01_001_1.ome.tif_dna.tif', '../20160708_I01_001_1.ome.tif_struct.tif', '../20160708_I01_001_1.ome.tif_cell.tif'])
