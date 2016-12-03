from PIL import Image
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
        # this is dumb but this is the way to make the file close correctly with Py3.5 :(
        # sorry future programmer
        with open(self.filePath, 'rb') as image_file:
            with Image.open(image_file) as image:
                return scipy.misc.fromimage(image)
