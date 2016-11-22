from scipy.misc import imsave
import numpy as np

class PngWriter:
    """
    Save a png
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

    # Assumes data is xyz where z is rgba, rgb, or r
    def save(self, data):
        shape = data.shape
        assert len(shape) == 3 or len(shape) == 2
        if len(shape) == 3:
            assert shape[2] == 3 or shape[2] == 4 or shape[2] == 1
        if shape[2] == 1:
            data = np.repeat(data, repeats=3, axis=2)
        imsave(self.filePath, data)

    def save_image(self, data, z=0, c=0, t=0):
        self.save(data)
