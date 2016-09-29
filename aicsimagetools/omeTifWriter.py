import omexml
import os
import tifffile


class OmeTifWriter:
    """
    assumes XYCZT ordering for now
    """

    def __init__(self, file_path):
        # nothing yet!
        self.filePath = file_path
        self.tif = tifffile.TiffWriter(self.filePath)
        self.omeMetadata = omexml.OMEXML()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.tif.close()

    # Assumes data is xyczt or xycz or xyz
    def save(self, data, channel_names=None, image_name="IMAGE0", pixels_physical_size=None):
        self._makeMeta(data, channel_names=channel_names, image_name=image_name, pixels_physical_size=pixels_physical_size)
        shape = data.shape
        xml = self.omeMetadata.to_xml()

        # check data shape for xyczt or xycz or xyz
        if len(shape) == 5:
            for i in range(self.size_t()):
                for j in range(self.size_z()):
                    for k in range(self.size_c()):
                        self.tif.save(data[i, j, k, :, :], compress=9, description=xml)
        elif len(shape) == 4:
            for i in range(self.size_z()):
                for j in range(self.size_c()):
                    self.tif.save(data[i, j, :, :], compress=9, description=xml)
        elif len(shape) == 3:
            for i in range(self.size_z()):
                self.tif.save(data[i, :, :], compress=9, description=xml)
        else:
            print "Data expected to have shape length 3, 4, or 5 but does not."

    def save_image(self, data, z=0, c=0, t=0):
        # assume this is one data slice of x by y
        assert len(data.shape) == 2
        assert data.shape[0] == self.size_y()
        assert data.shape[1] == self.size_x()
        # index = c + (self.size_c() * z) + (self.size_c() * self.size_z() * t)
        # tifffile interface only lets me write the next consecutive piece of data.
        self.tif.save(data, compress=9)

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
    def _makeMeta(self, data, channel_names=None, image_name="IMAGE0", pixels_physical_size=None):
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

        pixels.set_DimensionOrder('XYCZT')

        pixels.set_PixelType(data.dtype.name)

        if channel_names is None:
            for i in range(pixels.SizeC):
                pixels.Channel(i).set_ID("Channel:0:"+str(i))
                pixels.Channel(i).set_Name("C:"+str(i))
        else:
            for i, name in enumerate(channel_names):
                pixels.Channel(i).set_ID("Channel:0:"+str(i))
                pixels.Channel(i).set_Name(name+":"+str(i))

        # assume 1 sample per channel
        for i in range(pixels.SizeC):
            pixels.Channel(i).set_SamplesPerPixel(1)

        # many assumptions in here: one file per image, one plane per tiffdata, etc.
        pixels.populate_TiffData(os.path.basename(self.filePath))

        return ox
