from aicsimagetools import omexml
import tifffile
import numpy as np



class OmeTifReader:
    """
    assumes TZCYX ordering for now
    """

    def __init__(self, file_path):
        self.filePath = file_path
        try:
            self.tif = tifffile.TiffFile(self.filePath)
        except ValueError:
            raise AssertionError("File is not a valid file type")
        except IOError:
            raise AssertionError("File is empty or does not exist")
        if 'image_description' in self.tif.pages[0].tags:
            d = self.tif.pages[0].tags['image_description'].value.strip()
            assert d.startswith(b'<?xml version=') and d.endswith(b'</OME>')
            self.omeMetadata = omexml.OMEXML(d)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.tif.close()

    def load(self):
        data = self.tif.asarray()
        # Expand return to have time value of 1
        return np.expand_dims(data, axis=0)

    def load_slice(self, z=0, c=0, t=0):
        index = c + (self.size_c() * z) + (self.size_c() * self.size_z() * t)
        data = self.tif.asarray(key=index)
        return data

    def get_metadata(self):
        return self.omeMetadata

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

    def dtype(self):
        return self.tif.pages[0].dtype
