from aicsimagetools import *
import numpy as np
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

    return im


def arrange(projz, projy, projx, sx, sy, sz):
    #                            439, 167, 5
    # assume all images are shape [x,y,3]
    # do stuff and return big image
    shZ = projz.shape
    shX = projx.shape
    shY = projy.shape
    assert (len(shZ) == len(shY) == len(shX) == 3)

    im_all = np.zeros((3, sy+sz, sx+sz))
    print(im_all.shape)
    # im_all = np.zeros(np.hstack((sx+sz, sy+sz, 3)))
    # put in projx
    im_all[:, :sz, :sy] = projx
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


def im2_projection(im1, opts, out_file='output.png'):
    # im: either a 4d numpy array as CZYX, list of 3d ZYX np arrays, or list of 2d YX np arrays
    # opts: dict with options
    # - method, str. 'mean', 'sum', 'max', or 'slice'. max by default
    # - proj_all, true gives all 3 projections, false just gives xy. false by default
    # - contrast_type, 'none', 'local', or 'global'. none by default

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

    if 'colors' not in opts or opts['colors']:
        print("Error: invalid color option")
        return

    # scale colors down to 0-1 range if they're bigger than 1
    if any(v > 1 for v in np.array(opts['colors']).flatten()):
        colors = []
        for i in range(3):
            colors.append([v / 255 for v in opts['colors'][i]])
    else:
        colors = opts['colors']

    # apply color mask
    for i in range(3):
        im[i] *= colors[i]

    # only do xy proj
    if 'proj_all' not in opts or opts['proj_all'] == False:
        img_final = matproj(im, 1, opts.get('method', 'max'), im.shape[1] // 2)
    else:
        # xy, xz, yz projections (in that order)
        proj_z, proj_y, proj_x = (matproj(im, i, opts.get('method', 'max'), im.shape[i] // 2) for i in range(1,4))

        # perform local contrast adjustment
        if opts.get('contrast_type', '') == 'local':
            proj_z, proj_y, proj_x = map(lambda p: p / np.max(p.flatten()), (proj_z, proj_y, proj_x))

        # 439, 167, 5
        img_final = arrange(proj_z, proj_y, proj_x, proj_z.shape[2], proj_z.shape[1], proj_y.shape[1])

    if opts.get('global', '') == 'global':
        img_final /= np.max(img_final.flatten())
    with pngWriter.PngWriter(out_file) as png:
        print(proj_z.shape)
        png.save(img_final)


with omeTifReader.OmeTifReader('../multi-channel-z-series.ome.tif') as reader:
    img = reader.load()[0]
    print(img.shape)
    im2_projection(img, {'colors': [[1.0,1.0,1.0],[1.0,1.0,1.0],[1.0,1.0,1.0]]})

