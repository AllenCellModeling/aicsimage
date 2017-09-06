import numpy as np
from PIL import image


def normalize_image_zero_one(im):
    im -= np.min(im)
    if np.max(im) != 0:
        im /= np.max(im)
    return (im)


# im should be a numpy array
def float_to_eight_bit(im, dtype=np.uint8):

    imax = np.iinfo(dtype).max + 1  # imax = 256 for uint8
    im = im * imax
    im[im == imax] = imax - 1

    im = np.asarray(im, dtype)

    return (im)


def quantile_projection(img, proj_axis=2, projection_quantile=100, clip_quantile=100, ave_mix_in=0):

    in_dims = img.shape[1:]  # ignore channel dim
    out_dims = in_dims[:proj_axis] + in_dims[proj_axis + 1:]  # skip axis on which we're projecting
    height, width = out_dims

    final_img = np.zeros([height, width, 3], dtype=np.uint8)

    # channel indices:
    # 0: cell segmentation
    # 1: nuclear segmentation
    # 2: dna channel
    # 3: mambrane channel
    # 4: structure channel
    # 5: bright-field

    for i, c in enumerate([3, 4, 2]):
        im_c_3d = img[c, :, :, :]

        # analagous to max project but choose a quantile level instead, so remove outliers
        im_c = np.percentile(im_c_3d, projection_quantile, axis=proj_axis)
        im_c = normalize_image_zero_one(im_c)

        # maybe mix in some average projection
        if ave_mix_in > 0:
            av_proj = np.average(im_c_3d, axis=proj_axis)
            av_proj = normalize_image_zero_one(av_proj)
            im_c = (1 - ave_mix_in) * im_c + ave_mix_in * av_proj

        # remove extreme bright spots by setting them equal to some threshold, ingore zeros in quantile level
        if np.max(im_c) > 0:
            im_c = np.clip(im_c, a_min=0, a_max=np.percentile(im_c[im_c > 0], clip_quantile))

        #normalize again after clipping
        im_c = normalize_image_zero_one(im_c)

        # normalize to [0,1] and convert to graphics friendly data range/type
        im_c = float_to_eight_bit(im_c)

        # save as part of rgb array
        final_img[:, :, i] = im_c

    return (final_img)


def image_from_array(arr):
    img = Image.fromarray(arr, 'RGB')
    return (img)
