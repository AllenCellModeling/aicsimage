# author: Zach Crabtree zacharyc@alleninstitute.org

import numpy as np

from aicsimage.io import omeTifReader, cziReader


# TODO if this is good, we should refactor the other processing modules to use it
class CellImage:
    default_dims = "TCZYX"

    def __init__(self, data, **kwargs):
        self.dims = CellImage.default_dims
        if isinstance(data, str):
            # input is a filepath
            self.file_path = data

            # check for compatible data types
            if data.endswith(".czi"):
                self.reader = cziReader.CziReader(self.file_path)
            elif data.endswith(".ome.tif") or data.endswith(".ome.tiff"):
                self.reader = omeTifReader.OmeTifReader(self.file_path)
            else:
                raise ValueError("CellImage can only accept OME-TIFF and CZI file formats!")

            # TODO remove this transpose call once readers are fixed
            self.data = self.reader.load().transpose(0, 2, 1, 3, 4)
            self.metadata = self.reader.get_metadata()
            # internal data should always be stored as TCZYX
            self._generate_size()

        elif isinstance(data, np.ndarray):
            # input is a data array
            self.data = data

            if "dims" not in kwargs:
                raise ValueError("Must provide dims parameter when instantiating CellImage object from array!")

            if self.is_valid_dimension(kwargs["dims"]):
                self.dims = kwargs["dims"]

            if len(self.dims) != len(self.data.shape):
                raise ValueError("Number of dimensions must match dimensions of array provided!")

            self._generate_size()

    def is_valid_dimension(self, dimensions):
        if dimensions.strip(self.dims):
            # dims contains more than the standard 5 dims we're used to
            raise ValueError("{} contains invalid dimensions!".format(dimensions))

        count = {}
        for char in dimensions:
            if char in count:
                raise ValueError("{} contains duplicate dimensions!".format(dimensions))
            else:
                count[char] = 1

        return True

    def _generate_size(self):
        self.shape = []
        # create a map of dimensions -> value in the data array that was passed in originally
        dim_map = {self.dims[i]: self.data.shape[i] for i in range(len(self.dims))}
        for dim in CellImage.default_dims:
            self.shape.append(dim_map.get(dim, 1))
        self.size_t, self.size_c, self.size_z, self.size_y, self.size_x = tuple(self.shape)


    def get_image_data(self, out_orientation="TCZYX", **kwargs):
        """

        :param out_orientation:
        :param kwargs: These will contain the dims you exclude from out_orientation. If you all ZYX at T = 0 and C = 3, you will
        add a kwarg with C=3 and T=0 (each dimension not included will default to 0).
        :return: ndarray with dimension ordering that was specified with out_orientation
        """
        image_data = self.data
        if out_orientation != self.dims and self.is_valid_dimension(out_orientation):
            # map each dimension (TCZYX) to its index in out_orientation
            match_map = {dim: out_orientation.find(dim) for dim in self.dims}
            slicer, transposer = [], []
            for dim in self.dims:
                if match_map[dim] == -1:
                    # only get the bottom slice of this dimension, unless the user specified another in the args
                    slice_value = kwargs.get(dim, 0)
                    if slice_value >= self.shape[self.dims.find(dim)] or slice_value < 0:
                        raise ValueError("{} is not a valid index for the {} dimension".format(slice_value, dim))
                    slicer.append(slice_value)
                else:
                    # append all slices of this dimension
                    slicer.append(slice(None, None))
                    transposer.append(match_map[dim])
            image_data = image_data[slicer].transpose(transposer)

        return image_data