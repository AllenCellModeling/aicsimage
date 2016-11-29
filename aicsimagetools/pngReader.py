import scipy.misc


class PngReader:
    """
    Load a png
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

    # Assumes data is xyz where z is rgba, rgb, or r
    def load(self):
        return scipy.misc.imread(self.filePath)
