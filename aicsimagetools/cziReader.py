import czifile


class CziReader:
    """
    Load a png
    """

    def __init__(self, file_path):
        # nothing yet!
        self.filePath = file_path
        self.czi = czifile.CziFile(self.filePath)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.czi.close()

    def load(self):
        data = self.czi.asarray()
        return data

    def load_image(self, z=0, c=0, t=0):
        # assume c-z-t precedence
        # assume stacks are in Z, c and t are always 0
        index = c + (self.size_c() * z) + (self.size_c() * self.size_z() * t)
        data = self.czi.asarray()
        return data

    def get_metadata(self):
        return self.czi.metadata

    def size_z(self):
        return self.czi.shape[2]

    def size_c(self):
        return self.czi.shape[1]

    def size_t(self):
        return self.czi.shape[0]

    def size_x(self):
        return self.czi.shape[4]

    def size_y(self):
        return self.czi.shape[3]

    def dtype(self):
        return self.czi.dtype
