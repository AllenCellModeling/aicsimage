# author: Zach Crabtree zacharyc@alleninstitute.org

from skimage import measure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import aicsImage


class CellMesh:

    def __init__(self, verts, faces, normals, values, base_image):
        self.verts = verts
        self.faces = faces
        self.normals = normals
        self.values = values
        if not isinstance(base_image, aicsImage.AICSImage):
            raise ValueError("CellMesh only accepts a CellImage as its base_image parameter")
        self.image_stack = base_image

    def display(self):
        # Display resulting triangular mesh using Matplotlib. This can also be done
        # with mayavi (see skimage.measure.marching_cubes docstring).
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Fancy indexing: `verts[faces]` to generate a collection of triangles
        mesh = Poly3DCollection(self.verts[self.faces])
        mesh.set_edgecolor('k')
        ax.add_collection3d(mesh)

        ax.set_xlim(0, self.image_stack.size_x)
        ax.set_ylim(0, self.image_stack.size_y)
        ax.set_zlim(0, self.image_stack.size_z)

        plt.tight_layout()
        plt.show()

    def save_as_obj(self, file_path):
        with open(file_path, "w") as writer:
            writer.write("# OBJ file\n")
            writer.write("o Name\n")
            for v in self.verts:
                writer.write("v {:.6f} {:.6f} {:.6f}\n".format(v[0], v[1], v[2]))
            for n in self.normals:
                writer.write("vn {:.6f} {:.6f} {:.6f}\n".format(n[0], n[1], n[2]))
            for f in self.faces:
                writer.write("f {} {} {}\n".format(f[0], f[1], f[2]))


def generate_mesh(image, isovalue=0, channel=0):
    # image must be an AICSImage object
    image_stack = image.get_image_data("ZYX", C=channel)
    # Use marching cubes to obtain the surface mesh of the membrane wall
    verts, faces, normals, values = measure.marching_cubes(image_stack, 1, allow_degenerate=False, use_classic=True)
    return CellMesh(verts, faces, normals, values, image)

