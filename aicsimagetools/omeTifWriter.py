from aicsimagetools import omexml
import os
import tifffile


class OmeTifWriter:
    """This class can take arrays of pixel values and do the necessary metadata creation to write them
    properly in OME xml format.

    Example:
        image = numpy.ndarray([1, 10, 3, 1024, 2048])
        # There needs to be some sort of data inside the image array
        writer = omeTifWriter.OmeTifWriter(path="file.ome.tif")
        writer.save(image)

        image2 = numpy.ndarray([5, 486, 210])
        # There needs to be some sort of data inside the image2 array
        with omeTifWriter.OmeTifWriter(path="file2.ome.tif") as writer2:
            writer2.save(image2)

        # Convert a CZI file into OME Tif.
        reader = cziReader.CziReader(path="file3.czi")
        writer = omeTifWriter.OmeTifWriter(path="file3.ome.tif")
        writer.save(reader.load())

    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.omeMetadata = omexml.OMEXML()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        pass

    def save(self, data, channel_names=None, image_name="IMAGE0", pixels_physical_size=None, channel_colors=None,
             overwrite_file=False):
        """Save an image with the proper OME xml metadata.

        :param data: An array of dimensions TZCYX, ZCYX, or CYX to be written out to a file.
        :param channel_names: The names for each channel to be put into the OME metadata
        :param image_name: The name of the image to be put into the OME metadata
        :param pixels_physical_size: The physical size of each pixel in the image
        :param channel_colors: The channel colors to be put into the OME metadata
        :param overwrite_file: If the file exists and this arg is True, the file will be overwritten
        """

        if overwrite_file and os.path.isfile(self.file_path):
            os.remove(self.file_path)
        elif os.path.isfile(self.file_path):
            raise IOError("File exists but user has chosen not to overwrite it.")

        tif = tifffile.TiffWriter(self.file_path)

        shape = data.shape
        assert (len(shape) == 5 or len(shape) == 4 or len(shape) == 3)

        self._make_meta(data, channel_names=channel_names, image_name=image_name,
                        pixels_physical_size=pixels_physical_size, channel_colors=channel_colors)
        xml = self.omeMetadata.to_xml()

        # check data shape for TZCYX or ZCYX or ZYX
        if len(shape) == 5:
            for i in range(self.size_t()):
                for j in range(self.size_z()):
                    for k in range(self.size_c()):
                        tif.save(data[i, j, k, :, :], compress=9, description=xml)
        elif len(shape) == 4:
            for i in range(self.size_z()):
                for j in range(self.size_c()):
                    tif.save(data[i, j, :, :], compress=9, description=xml)
        elif len(shape) == 3:
            for i in range(self.size_z()):
                tif.save(data[i, :, :], compress=9, description=xml)

        tif.close()

    def save_slice(self, data, z=0, c=0, t=0):
        """ this doesn't do the necessary functionality at this point

        TODO:
            * make this insert a YX slice in between two other slices inside a full image
            * data should be a 5 dim array

        :param data:
        :param z:
        :param c:
        :param t:
        :return:
        """
        assert len(data.shape) == 2
        assert data.shape[0] == self.size_y()
        assert data.shape[1] == self.size_x()
        tif = tifffile.TiffWriter(self.file_path)
        tif.save(data, compress=9)
        tif.close()

    def set_metadata(self, ome_metadata):
        self.omeMetadata = ome_metadata

    def size_z(self):
        return self.omeMetadata.image().Pixels.SizeZ

    def size_c(self):
        return self.omeMetadata.image().Pixels.SizeC

    def size_t(self):
        return self.omeMetadata.image().Pixels.SizeT

    def size_x(self):
        return self.omeMetadata.image().Pixels.SizeX

    def size_y(self):
        return self.omeMetadata.image().Pixels.SizeY

    # set up some sensible defaults from provided info
    def _make_meta(self, data, channel_names=None, image_name="IMAGE0", pixels_physical_size=None, channel_colors=None):
        """Creates the necessary metadata for an OME tiff image

        :param data: An array of dimensions TZCYX, ZCYX, or CYX to be written out to a file.
        :param channel_names: The names for each channel to be put into the OME metadata
        :param image_name: The name of the image to be put into the OME metadata
        :param pixels_physical_size: The physical size of each pixel in the image
        :param channel_colors: The channel colors to be put into the OME metadata
        """
        ox = self.omeMetadata

        ox.image().set_Name(image_name)
        ox.image().set_ID("0")
        pixels = ox.image().Pixels
        pixels.ome_uuid = ox.uuidStr
        pixels.set_ID("0")
        if pixels_physical_size is not None:
            pixels.set_PhysicalSizeX(pixels_physical_size[0])
            pixels.set_PhysicalSizeY(pixels_physical_size[1])
            pixels.set_PhysicalSizeZ(pixels_physical_size[2])
        shape = data.shape
        if len(shape) == 5:
            pixels.channel_count = shape[2]
            pixels.set_SizeT(shape[0])
            pixels.set_SizeZ(shape[1])
            pixels.set_SizeC(shape[2])
            pixels.set_SizeY(shape[3])
            pixels.set_SizeX(shape[4])
        elif len(shape) == 4:
            pixels.channel_count = shape[1]
            pixels.set_SizeT(1)
            pixels.set_SizeZ(shape[0])
            pixels.set_SizeC(shape[1])
            pixels.set_SizeY(shape[2])
            pixels.set_SizeX(shape[3])
        elif len(shape) == 3:
            pixels.channel_count = 1
            pixels.set_SizeT(1)
            pixels.set_SizeZ(shape[0])
            pixels.set_SizeC(1)
            pixels.set_SizeY(shape[1])
            pixels.set_SizeX(shape[2])

        # this must be set to the *reverse* of what dimensionality the ome tif file is saved as
        pixels.set_DimensionOrder('XYCZT')
        pixels.set_PixelType(data.dtype.name)

        if channel_names is None:
            for i in range(pixels.SizeC):
                pixels.Channel(i).set_ID("Channel:0:"+str(i))
                pixels.Channel(i).set_Name("C:"+str(i))
        else:
            for i, name in enumerate(channel_names):
                pixels.Channel(i).set_ID("Channel:0:"+str(i))
                pixels.Channel(i).set_Name(name)

        if channel_colors is not None:
            assert len(channel_colors) == pixels.get_SizeC()
            for i in range(len(channel_colors)):
                pixels.Channel(i).set_Color(channel_colors[i])

        # assume 1 sample per channel
        for i in range(pixels.SizeC):
            pixels.Channel(i).set_SamplesPerPixel(1)

        # many assumptions in here: one file per image, one plane per tiffdata, etc.
        pixels.populate_TiffData(os.path.basename(self.file_path))

        return ox
