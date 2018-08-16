import numpy as np
import scipy.ndimage

def normalize_img(img, mask=None, method='img_bg_sub'):
    
    img = img.astype(float)
    
    if mask is None:
        mask = np.ones(img.shape)
        
    if method is 'img_bg_sub':
        im_f = scipy.ndimage.gaussian_filter(img, sigma=0.5)
        prct = np.percentile(im_f[mask>0], 50)
        
        im_f = im_f - prct
        im_out = img - prct
        
        im_f[im_f<0] = 0
        im_out[im_out<0] = 0
        
        im_out = im_out/np.max(im_f)
        
        im_out[im_out<0] = 0
        im_out[im_out>1] = 1
    
    elif method is 'trans': #transmitted
        #Normalizes to 0.5, with std of 0.1
        im_f = scipy.ndimage.gaussian_filter(img, sigma=0.5)
        mu = np.mean(im_f)
        std = np.std(im_f)
        
        std_fract = 10
        
        im_out = (img - mu) / (std*std_fract) + 0.5
        
        im_out[im_out<0] = 0
        im_out[im_out>1] = 1
        
    elif method is None or method is 'none':
        pass
    else:
        raise NotImplementedError
    
    
    return im_out
    
    

def mask_normalization(image, mask, method):
    raise NotImplementedError