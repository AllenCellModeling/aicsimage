import numpy as np

import czifile


class CziReader:
    """This class is used primarily for opening and processing the contents of a CZI file

    Example:
        reader = cziReader.CziReader(path="file.czi")
        file_image = reader.load()
        file_slice = reader.load_slice(t=1, z=2, c=3)

        with cziReader.CziReader(path="file2.czi") as reader:
            file2_image = reader.load()
            file2_slice = reader.load_slice(t=1, z=2, c=3)

        # Convert a CZI file into OME Tif.
        reader = cziReader.CziReader(path="file3.czi")
        writer = omeTifWriter.OmeTifWriter(path="file3.ome.tif")
        writer.save(reader.load())

    The load() function gathers all the slices into a single 5d array with dimensions TZCYX.
    This should be used when the entire image needs to be processed or transformed in some way.

    The load_slice() function takes a single 2D slice with dimensions YX out of the 5D image.
    This should be used when only a few select slices need to be processed
    (e.g. printing out the middle slice for a thumbnail image)

    This class has a similar interface to OmeTifReader.

    In order to better understand the inner workings of this class, it is necessary to
    know that CZI files can be abstracted as an n-dimensional array.

    CZI files contain an n-dimensional array.
    If t = 1, then the array will be 6 dimensional 'BCZYX0' (czifile.axes)
    Otherwise, the array will be 7 dimensional 'BTCZYX0' (czifile.axes)
    'B' is block acquisition from the CZI memory directory
    'T' is time
    'C' is the channel
    'Z' is the index of the slice in the image stack
    'X' and 'Y' correspond to the 2D slices
    '0' is the numbers of channels per pixel (always =zero for our data)
    """

    def __init__(self, file_path):
        """
        :param file_path(str): The path for the file that is to be opened.
        """
        self.filePath = file_path
        self.czi = czifile.CziFile(self.filePath)
        self.hasTimeDimension = len(self.czi.shape) == 7

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.czi.close()

    def close(self):
        self.czi.close()

    def load(self):
        """Retrieves an array for all z-slices and channels.

        :return: 5D array with dimensions TZCYX.
        """
        image = self.czi.asarray()

        if self.hasTimeDimension:
            transposed_image = image[0, :, :, :, :, :, 0]
            # returns array with dimensions 'TZCYX'
            return np.transpose(transposed_image, (0, 2, 1, 3, 4))
        else:
            transposed_image = image[0, :, :, :, :, 0]
            # returns array with dimensions 'ZCYX'
            return np.expand_dims(np.transpose(transposed_image, (1, 0, 2, 3)), 0)

    def load_slice(self, z=0, c=0, t=0):
        """Retrieves the 2D YX slice from the image

        :param z: The z index that will be accessed
        :param c: The channel that will be accessed
        :param t: The time index that will be accessed
        :return: 2D array with dimensions YX
        """
        if self.hasTimeDimension:
            for directory_entry in self.czi.filtered_subblock_directory:
                if directory_entry.start[3] == z and directory_entry.start[2] == c and directory_entry.start[1] == t:
                    # tile is a slice with all seven dimensions (BTCZYX0) still intact
                    tile = directory_entry.data_segment().data()
                    image_slice = tile[0, 0, 0, 0, :, :, 0]
                    return image_slice
        else:
            for directory_entry in self.czi.filtered_subblock_directory:
                if directory_entry.start[2] == z and directory_entry.start[1] == c:
                    # tile is a slice with all six dimensions (BCZYX0) still intact
                    tile = directory_entry.data_segment().data()
                    image_slice = tile[0, 0, 0, :, :, 0]
                    return image_slice

    def get_metadata(self):
        return self.czi.metadata

    def size_z(self):
        return self.czi.shape[3] if self.hasTimeDimension else self.czi.shape[2]

    def size_c(self):
        return self.czi.shape[2] if self.hasTimeDimension else self.czi.shape[1]

    def size_t(self):
        return self.czi.shape[1] if self.hasTimeDimension else 1

    def size_x(self):
        return self.czi.shape[5] if self.hasTimeDimension else self.czi.shape[4]

    def size_y(self):
        return self.czi.shape[4] if self.hasTimeDimension else self.czi.shape[3]

    def dtype(self):
        return self.czi.dtype
