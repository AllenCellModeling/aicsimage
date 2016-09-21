aicsimagetools
--------------

A collection of Reader/Writer classes to get data into and out of numpy arrays.

Reader.load or Reader.load_image
Writer.save or Writer.save_image

PngRW, OmeTifRW, TifR, CziR

Currently depends on tifffile and czifile from
http://www.lfd.uci.edu/~gohlke/code/tifffile.py.html
http://www.lfd.uci.edu/~gohlke/code/czifile.py.html

To use (with caution), simply do::

    >>> import aicsimagetools
    >>> do stuff with images
