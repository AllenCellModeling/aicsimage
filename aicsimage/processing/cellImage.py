# author: Zach Crabtree zacharyc@alleninstitute.org

import numpy as np

from aicsimage.io import omeTifReader, cziReader


# TODO if this is good, we should refactor the other processing modules to use it
class CellImage:

    def __init__(self, data, **kwargs):
        # TODO take in file paths, arrays of various sizes (rearrange dims)
        if isinstance(data, str):
            # input is a filepath
            self.file_path = data
            if data.endswith(".czi"):
                self.reader = cziReader.CziReader(self.file_path)
            elif data.endswith(".ome.tif") or data.endswith(".ome.tiff"):
                self.reader = omeTifReader.OmeTifReader(self.file_path)
            else:
                raise ValueError("CellImage can only accept OME-TIFF and CZI file formats!")
            self.metadata = self.reader.get_metadata()
            self._generate_size()
            # should always default to TCZYX
            self.dims = "TCZYX"
        elif isinstance(data, np.ndarray):
            # input is a data array
            self.data = data
            if "dims" not in kwargs:
                raise ValueError("Must provide dims parameter when instantiating CellImage object from array!")
            self.dims = kwargs["dims"]
            if len(self.dims) != len(self.data.shape):
                raise ValueError("Number of dimensions must match dimensions of array provided!")
            self._generate_size()

    def _generate_size(self):
        if hasattr(self, 'file_path'):
            # this object was constructed from a file path
            self.size_t = self.reader.size_t()
            self.size_c = self.reader.size_c()
            self.size_z = self.reader.size_z()
            self.size_y = self.reader.size_y()
            self.size_x = self.reader.size_x()
        elif hasattr(self, 'data'):
            # this object was constructed from an array
            dim_list = list(self.dims)
            # create a map of dimensions to value in the data array that was passed in originally
            dim_map = {dim_list[i]: self.data.shape[i] for i in range(len(dim_list))}
            self.size_t = dim_map.get("T", 1)
            self.size_c = dim_map.get("C", 1)
            self.size_z = dim_map.get("Z", 1)
            self.size_y = dim_map.get("Y", 1)
            self.size_x = dim_map.get("X", 1)

        self.shape = [self.size_t, self.size_c, self.size_z, self.size_y, self.size_x]

    def get_image_data(self, out_orientation="TCZYX"):
        if hasattr(self, 'file_path'):
            # this object was constructed from a file path
            # TODO remove this transpose call after reader changes because the reader loads TZCYX currently
            image_data = self.reader.load().transpose(0, 2, 1, 3, 4)
        elif hasattr(self, 'data'):
            # this object was constructed from an array
            image_data = self.data
        else:
            # this error should never be thrown
            raise ValueError("This CellImage object was not instantiated correctly!")
        if out_orientation != self.dims:
            if out_orientation.strip("TCZYX"):
                # dims contains more than the standard 5 dims we're used to
                raise ValueError("%s contains invalid dimensions!".format(out_orientation))
            count = {}
            for char in out_orientation:
                if char in count:
                    raise ValueError("%s contains duplicate dimensions!".format(out_orientation))
                else:
                    count[char] = 1
            # map each dimension (TCZYX) to its index in out_orientation
            match_map = {dim: out_orientation.find(dim) for dim in self.dims}
            slicer, transposer = [], []
            for dim in self.dims:
                if match_map[dim] == -1:
                    slicer.append(0)
                else:
                    slicer.append(slice(None, None))
                    transposer.append(match_map[dim])
            image_data = image_data[slicer].transpose(transposer)

        return image_data