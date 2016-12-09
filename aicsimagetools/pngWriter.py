from scipy.misc import imsave
import numpy as np


class PngWriter:
    """
    Saves a png
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
        # check for rgb, rgba, or r
        if len(data.shape) == 3:
            assert data.shape[0] == 4 or data.shape[0] == 3 or data.shape[0] == 1
            # if three dimensions, transpose to YXC (imsave() needs it in these axes)
            data = np.transpose(data, (1, 2, 0))
            # if there's only one channel, repeat across the next two channels
            if data.shape[2] == 1:
                data = np.repeat(data, repeats=3, axis=2)
        elif len(data.shape) != 2:
            raise ValueError("Data was not of dimensions CYX or YX")

        imsave(self.filePath, data)

    # data is CYX or YX array
    def save_slice(self, data, z=0, c=0, t=0):
        self.save(data)
