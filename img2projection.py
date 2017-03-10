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
    # put in projx
    im_all[:, :sy, :sz] = projx
    # put in projz
    im_all[:, :sy, sz:] = projz
    im_all[:, sy:, sz:] = projy

    # if rescale_inten:
    #     im_all /= np.max(im_all.flatten())

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


def im2projection(im1, proj_all = False, proj_method ='max', colors = lambda i: [1, 1, 1], color_adjust = False, contrast_type = "none"):
    # im: either a 4d numpy array as CZYX, list of 3d ZYX np arrays, or list of 2d YX np arrays
    # method, str. 'mean', 'sum', 'max', or 'slice'. max by default
    # proj_all, true gives all 3 projections, false just gives xy. false by default
    # contrast_type, 'none', 'local', or 'global'. none by default
    # adjust, boolean, whether to scale colors down to 0-255 range. false by default

    # TODO: turn this into one-liner with np.cat?
    # turn list of 2d or 3d arrays into single 4d array if needed
    try:
        if type(im1) == type([]):
            # if only YX, add a single Z dimen
            if im1[0].ndim == 2:
                im1 = list(map(lambda a: np.expand_dims(a,axis=0), im1))
            elif im1[0].ndim != 3:
                print("Error: im1 must be a list of 2d or 3d arrays")
                return
            # combine list into 4d array
            im = np.stack(im1)
        else:
            if im1.ndim != 4:
                print("Error: invalid dimensions for im1")
                return
            im = im1

    except (AttributeError, IndexError):
        # its not a list of np arrays
        print("Error: im1 must be either a 4d numpy array or a list of numpy arrays")
        return

    # color processing code
    # if 'colors' not in opts:
    #     print("Error: missing color option")
    #     return
    if isinstance(colors, str):
        # pass it in to matplotlib
        try:
            colors = pplot.get_cmap(colors)(np.linspace(0,1,len(im)))
        except ValueError:
            # thrown when string is not valid function
            print("Error: Invalid cmap string")
            return
    elif callable(colors):
        # if its a function
        try:
            colors = [colors(i) for i in range(len(im))]
        except TypeError:
            print("Error: Invalid color function")
            return

    # else, were assuming it s a list
    # scale colors down to 0-1 range if they're bigger than 1
    if any(v > 1 for v in np.array(colors).flatten()):
        # TODO: make this a one liner if possible
        new_colors = []
        for i in range(3):
            new_colors.append([v / 255 for v in colors[i]])
            colors = new_colors

    # create final image
    if not proj_all:
        img_final = np.zeros((3, im.shape[2], im.shape[3]))
    else:
        #                                 y + z,                     x + z
        img_final = np.zeros((3, im.shape[2]+ im.shape[1], im.shape[3] + im.shape[1]))

    img_piece = np.empty(img_final.shape)
    # loop through all channels
    for i, img_c in enumerate(im):
        # TODO: refactor a bit, its a little messy
        try:
            proj_z = matproj(img_c, 0, proj_method, im.shape[0] // 2)
            if proj_all:
                proj_y, proj_x = (matproj(img_c, axis, proj_method, im.shape[axis] // 2) for axis in range(1, 3))
                # flipping to get them facing the right way
                proj_x = np.fliplr(np.transpose(proj_x, (1, 0)))
                proj_y = np.flipud(proj_y)
                z_len = proj_y.shape[0]
        except ValueError:
            print("Error: Invalid projection function")
            return

        x_len = proj_z.shape[1]
        y_len = proj_z.shape[0]


        if proj_all:
            img_piece = arrange(proj_z, proj_y, proj_x, x_len, y_len, z_len)
        else:
            img_piece[:] = proj_z

        # TODO: can this be a one-liner?
        for c in range(3):
            img_piece[c] *= colors[i][c]

        img_final += img_piece

    # color range adjustment
    if color_adjust:
        # get max color value and scale all by that value if over max
        max_val = np.max(img_final.flatten())
        if max_val > 255:
            img_final /= max_val

    # global contrast adjustment
    if contrast_type == 'global':
        img_final /= np.max(img_final.flatten())

    return img_final



def test():
    # check that 4d array input works
    assert im2projection(np.ones((1, 3, 4, 5))).shape == (3, 4, 5)
    # but only a 4d
    assert im2projection(np.ones((1, 1, 3, 4, 5))) is None
    # check that 3d array list works
    assert im2projection([np.ones((3, 4, 5)), np.ones((3, 4, 5))]).shape == (3, 4, 5)
    # check that 2d array list works
    assert im2projection([np.ones((4, 5)), np.ones((4, 5))]).shape == (3, 4, 5)
    # but not a list of 1d arrays
    assert im2projection([np.array([1, 2, 3]), np.array([1, 2, 3])]) is None
    # has to be a numpy array
    assert im2projection([[[[1]]]]) is None

    # checking projection methods
    test_cube = np.empty((1, 6, 6, 6))
    color_fun = lambda i: [1, 1, 1]
    assert im2projection(test_cube, proj_method='max').shape == (3, 6, 6)
    assert im2projection(test_cube, proj_method='not-real') is None


def run(in_file):
    with omeTifReader.OmeTifReader(in_file) as reader:
        img = reader.load()
        out = im2projection(img, proj_all= True)
        with pngWriter.PngWriter('out.png', overwrite_file=True) as w:
            w.save(out)

run('../20160708_I01_001_1.ome.tif_memb.tif')
