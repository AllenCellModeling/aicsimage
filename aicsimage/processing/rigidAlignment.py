import numpy as np
import sklearn.decomposition
import scipy
from .alignMajor import align_major, angle_between

import pdb

# img - a CYXZ numpy array, channel order is generally [DNA, NUCLEUS, ... ]

def cell_rigid_registration(img, ch_crop = 1, ch_angle = 1, ch_com = 0, ch_flipdim = 1):
            
    #crop to rotate faster
    _, croprange = crop_img(get_channel(img, ch_crop))
    img = img[croprange]

    #rotate
    angle = get_major_angle(get_channel(img, ch_angle))

    angle = [[i, -j] for i, j in angle]  
    img = align_major(img, angle)
    
    _, croprange = crop_img(get_channel(img, ch_crop))
    img = img[croprange]
    
    #flipdim
    flipdim = get_flipdims(get_channel(img, ch_flipdim))
    img = flipdims(img, flipdim)

    img = pad_to_center(img, ch_crop, ch_com)

    return img, angle, flipdim
    
def cell_rigid_deregistration(img, flipdim_orig, angle_orig, com_orig, imsize_orig, ch_crop = 1, ch_com = 0):
    #deflip the image
    img = flipdims(img, flipdim_orig)

    #derotate the image
    angle = [[i, -j] for i, j in angle_orig]    
    img = align_major(img, angle)

    #depad the image
    img = pad_to_position(img, ch_crop, ch_com, com_orig, imsize_orig)

    return img
    
def get_channel(img, channel):
    return np.expand_dims(img[channel], 0)
        
def get_rigid_reg_stats(img, com_method = 'nuc'):
    imsize = img.shape
    com = get_com(img, com_method)

    return imsize, com, angle, flipdim
        
    
def get_major_angle(img):
    #align on the 2D projection
    if len(img.shape) == 4:
        img = np.sum(img, axis=3)
    
    pos = np.stack(np.where(img>0), axis=1)
    
    pca = sklearn.decomposition.PCA()    
    
    pca.fit(pos - np.mean(pos, axis=0))

    angles = np.array(pca.components_[0,1:3])
    
    angle = angle_between(angles, np.array([1,0]))
    
    if angles[1] < 0:
        angle = 360 - angle
    
    return [[int(0), angle]]

def flipdims(img, flipdim):
    for flip, i in zip(flipdim, range(len(flipdim))):
        if flip: 
            img = np.flip(img, i)

    #dont flip on z for the time being
    flipdim[-1] = 0
                
    return img

def get_com(img):

    com = np.mean(np.stack(np.where(img>0)), axis=1)
    
    return com
    
def crop_img(img):
    
    inds = np.stack(np.where(img>0))

    starts = np.min(inds, axis=1)
    ends = np.max(inds, axis=1)+1

    croprange = [slice(s, e) for s,e in zip(starts,ends)]
    #dont crop the channel dimension
    croprange[0] = slice(0,None)
    
    img_out = img[croprange]
    
    return img_out, croprange

def get_flipdims(img):
    skew = scipy.stats.skew(np.stack(np.where(img), axis=0), axis=1)
    skew[-1] = 0
    
    return skew < 0


def pad_to_position(img, ch_crop, ch_com, com_target, imsize_target):
    
    _, croprange_pt2 = crop_img(get_channel(img, ch_crop))
    img = img[croprange_pt2]
    
    com = get_com(get_channel(img, ch_com))
    
    pad_com = com-com_target
    
    pad_pre = (com_target - (com + 1) )[1:]
    pad_post = (imsize_target - com_target - (np.array(img.shape) - (com + 1)))[1:]
    
    pad_width = [[0,0]]
    
    for pre, post in zip(pad_pre, pad_post):
        pad_width += [[int(np.ceil(pre)), int(np.floor(post))]]
    
    img_out = np.pad(img, pad_width, mode='constant', constant_values=0)
    
    return img_out

    
def pad_to_center(img, ch_crop, ch_com):
    _, croprange_pt2 = crop_img(get_channel(img, ch_crop))
    img = img[croprange_pt2]

    com = get_com(get_channel(img, ch_com))
    
    pad_dims = img.shape - (com+1) - com

    img = pad_to_com(img, pad_dims)
    
    return img
   
def pad_to_com(img, pad_dims):
    pad_dims = pad_dims[1:].astype(int)
    #skip the channel dimension
    pad_width = [[0,0]]
    
    for i in pad_dims:
        if i > 0:
            pad = [[np.abs(i), 0]]
        else:
            pad = [[0, np.abs(i)]]
        
        pad_width += pad
    
    img = np.pad(img, pad_width, mode='constant', constant_values=0)
    
    return img