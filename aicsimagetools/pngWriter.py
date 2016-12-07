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

    # Assumes data is CYX where c is rgb, rgba, or r
    def save(self, data):
        shape = data.shape
        assert len(shape) == 3 or len(shape) == 2
        if len(shape) == 3:
            assert shape[0] == 3 or shape[0] == 4 or shape[0] == 1
        if shape[0] == 1:
            data = np.repeat(data, repeats=3, axis=2)
        data = np.transpose(data, (1, 2, 0))
        imsave(self.filePath, data)

    # data is CYX or YX array
    def save_slice(self, data, z=0, c=0, t=0):
        self.save(data)
