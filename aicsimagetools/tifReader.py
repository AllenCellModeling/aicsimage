import tifffile


class TifReader:
    """
    info
    """

    def __init__(self, file_path):
        # nothing yet!
        self.filePath = file_path
        self.tif = tifffile.TiffFile(self.filePath)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tif.close()

    def load(self):
        data = self.tif.asarray()
        return data

    def load_image(self, z=0, c=0, t=0):
        # assume c-z-t precedence
        # assume stacks are in Z, c and t are always 0
        # index = c + (self.size_c() * z) + (self.size_c() * self.size_z() * t)
        index = z
        data = self.tif.asarray(key=index)
        return data

    def get_metadata(self):
        return None

    def size_z(self):
        return len(self.tif.pages)

    def size_c(self):
        return 1

    def size_t(self):
        return 1

    def size_x(self):
        return self.tif.pages[0].shape[1]

    def size_y(self):
        return self.tif.pages[0].shape[0]

    def dtype(self):
        return self.tif.pages[0].dtype
