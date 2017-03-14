# Author: Evan Wiederspan

from aicsimagetools import *
import numpy as np
import matplotlib.pyplot as pplot
import scipy
import numbers

# taken from cellbrowser-tools thumbnail2.py


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


def arrange(projz, projy, projx, sx, sy, sz):
    #                            439, 167, 5
    # assume all images are shape [x,y,3]
    # do stuff and return big image
    shZ = projz.shape
    shX = projx.shape
    shY = projy.shape
    # assert (len(shZ) == len(shY) == len(shX) == 3)

    im_all = np.zeros((3, sy+sz, sx+sz))
    print(im_all.shape)
    # im_all = np.zeros(np.hstack((sx+sz, sy+sz, 3)))
    im_all[:, :sy, :sz] = projx
    im_all[:, :sy, sz:] = projz
    im_all[:, sy:, sz:] = projy

    return im_all


def make_rgb_proj(imzyx, axis, color, method='max', rescale_inten=True, slice_index=0):
    imdbl = np.asarray(imzyx).astype('double')
    # do projection
    im_proj = matproj(imdbl, axis, method, slice_index=slice_index)
    print(im_proj.shape)
    # turn into RGB
    # im_proj = np.expand_dims(im_proj, 2)
    # im_proj = np.repeat(im_proj, 3, 2)
 
    # inject color.  careful of type mismatches.
    im_proj[0, :, :] *= color[0]
    im_proj[1, :, :] *= color[1]
    im_proj[2, :, :] *= color[2]

    # if rescale_inten:
    #     maxval = np.max(im_proj.flatten())
    #     im_proj = im_proj / maxval    

    return im_proj


def im2projection(im1, proj_all=False, proj_method='max', colors=lambda i: [1, 1, 1], color_adjust=False, contrast_type="none"):
    # im: either a 4d numpy array as CZYX, list of 3d ZYX np arrays, or list of 2d YX np arrays
    # method, str. 'mean', 'sum', 'max', or 'slice'. max by default
    # proj_all, true gives all 3 projections, false just gives xy. false by default
    # contrast_type, 'none', 'local', or 'global'. none by default
    # color_adjust, boolean. If true, will scale each color channel independently to ensure that the max value is 255. False by default

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
                raise ValueError("invalid dimensions for im1")
            im = im1

    except (AttributeError, IndexError):
        # its not a list of np arrays
        raise ValueError("im1 must be either a 4d numpy array or a list of numpy arrays")

    # color processing code
    if isinstance(colors, str):
        # pass it in to matplotlib
        try:
            colors = pplot.get_cmap(colors)(np.linspace(0,1,len(im)))
        except ValueError:
            # thrown when string is not valid function
            raise ValueError("Invalid cmap string")
    elif callable(colors):
        # if its a function
        try:
            colors = [colors(i) for i in range(len(im))]
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
                img_piece = arrange(proj_z, proj_y, proj_x, proj_z.shape[1], proj_z.shape[0], proj_y.shape[0])
            else:
                img_piece[:] = proj_z
        except ValueError:
            raise ValueError("Invalid projection function")

        # TODO: can this be a one-liner?
        for c in range(3):
            img_piece[c] *= colors[i][c]

        img_final += img_piece

    # color range adjustment
    if color_adjust:
        # scale color channels independently
        for c in range(3):
            max_val = np.max(img_final[c].flatten())
            if max_val > 0:
                img_final[c] *= (255 / max_val)

    # global contrast adjustment
    if contrast_type == 'global':
        img_final /= np.max(img_final.flatten())
    elif contrast_type == 'local':
        z_len, y_len = im.shape[1:3]
        # TODO: research efficiency of this, it looks pretty slow
        img_final[:, :y_len, :z_len] /= np.max(img_final[:, :y_len, :z_len].flatten())
        img_final[:, :y_len, z_len:] /= np.max(img_final[:, :y_len, z_len:].flatten())
        img_final[:, y_len:, z_len:] /= np.max(img_final[:, y_len:, z_len:].flatten())

    return img_final


def test():
    def shouldThrow(f, *args, **kargs):
        try:
            f(*args, **kargs)
        except ValueError:
            return True
        return False
    # check that 4d array input works
    assert im2projection(np.empty((1, 3, 4, 5))).shape == (3, 4, 5)
    # any number of channels
    assert im2projection(np.empty((10, 3, 4, 5))).shape == (3, 4, 5)
    # but only a 4d
    assert shouldThrow(im2projection, np.empty((1, 1, 3, 4, 5)))
    # check that 3d array list works
    assert im2projection([np.empty((3, 4, 5)), np.empty((3, 4, 5))]).shape == (3, 4, 5)
    # check that 2d array list works
    assert im2projection([np.empty((4, 5)), np.empty((4, 5))]).shape == (3, 4, 5)
    # but not a list of 1d arrays
    assert shouldThrow(im2projection, [np.array([1, 2, 3]), np.array([1, 2, 3])])
    # has to be a numpy array
    assert shouldThrow(im2projection, [[[[1]]]])

    # checking projection methods
    test_cube = np.empty((1, 5, 5, 5))
    assert im2projection(test_cube, proj_method='max').shape == (3, 5, 5)
    assert shouldThrow(im2projection, test_cube, proj_method='not-real')

    # color methods
    assert im2projection(test_cube, colors='jet') is not None
    # only valid methods
    assert shouldThrow(im2projection, test_cube, colors='fake_func')
    # colors passed in as 0-255 should be scaled down
    assert (im2projection(np.ones((1, 5, 5, 5)), colors=[[255, 255, 255]])[0] == 1).all()
    # colors function should cancel out red channel
    assert (im2projection(test_cube, colors=lambda i: [0, 1, 1])[0] == 0).all()
    # color adjust should create some value at 255 in each channel
    # I do > 254 because it probably wont give a value that's exactly 255 due to floating point multiplication
    assert (im2projection(np.random.random((1, 5, 5, 5)), color_adjust=True)[0] > 254).any()


def run(in_files):
    img = [omeTifReader.OmeTifReader(f).load()[0] for f in in_files]
    out = im2projection(img, proj_all=True, proj_method='mean', colors='jet', color_adjust=True, contrast_type='global')
    with pngWriter.PngWriter('5-channel-global-contrast.png', overwrite_file=True) as w:
        w.save(out)
test()
# run(['../20160708_I01_001_1.ome.tif_memb.tif', '../20160708_I01_001_1.ome.tif_nuc.tif', '../20160708_I01_001_1.ome.tif_dna.tif', '../20160708_I01_001_1.ome.tif_struct.tif', '../20160708_I01_001_1.ome.tif_cell.tif'])
