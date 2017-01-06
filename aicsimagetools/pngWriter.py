from scipy.misc import imsave
import numpy as np
import os


class PngWriter:
    """This class can take 3D arrays of CYX pixel values and writes them to a png

    Example:
        image = numpy.ndarray([3, 1024, 2048])
        # There needs to be some sort of data inside the image array
        writer = pngWriter.PngWriter(path="file.png")
        writer.save(image)

        image2 = numpy.ndarray([3, 1024, 2048])
        # There needs to be some sort of data inside the image2 array
        with pngWriter.PngWriter(path="file2.png") as writer2:
            writer2.save(image2)
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        pass

    def save(self, data, overwrite_file=False):
        """Takes in an array of CYX pixel values and writes them to a png

        :param data: a CYX or YX array with C being the rgb channels for each pixel value
        :param overwrite_file: If the file exists and this arg is True, the file will be overwritten
        """

        if overwrite_file and os.path.isfile(self.file_path):
            os.remove(self.file_path)
        elif os.path.isfile(self.file_path):
            raise IOError("File exists but user has chosen not to overwrite it.")

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

        imsave(self.file_path, data)

    def save_slice(self, data, z=0, c=0, t=0, overwrite_file=False):
        """Exactly the same functionality as save() but allows the interface to be the same as OmeTifWriter

        :param data: a CYX or YX array with C being the rgb channels for each pixel value
        :param z: an arbitrary z index that does nothing
        :param c: an arbitrary c index that does nothing
        :param t: an arbitrary t index that does nothing
        :param overwrite_file: If the file exists and this arg is True, the file will be overwritten
        """
        self.save(data, overwrite_file=overwrite_file)
