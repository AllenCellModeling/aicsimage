from PIL import Image
import scipy.misc
import numpy as np


class PngReader:
    """
    Load a png
    """

    def __init__(self, file_path):
        # nothing yet!
        self.filePath = file_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        pass

    def load(self):
        # this is dumb but this is the way to make the file close correctly with Py3.5 :(
        # sorry future programmer
        with open(self.filePath, 'rb') as image_file:
            with Image.open(image_file) as image:
                # returns cyx where c is rgb, rgba, or r
                return np.transpose(scipy.misc.fromimage(image), (2, 0, 1))
