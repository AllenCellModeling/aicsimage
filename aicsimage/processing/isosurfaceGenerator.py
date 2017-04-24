# author: Zach Crabtree zacharyc@alleninstitute.org

from skimage import measure
from scipy.ndimage.interpolation import zoom
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import argparse

import aicsImage
import thumbnailGenerator


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
            for v in mesh.verts:
                writer.write("v {} {} {}\n".format(v[0], v[1], v[2]))
            for n in mesh.normals:
                writer.write("vn {} {} {}\n".format(n[0], n[1], n[2]))
            for f in mesh.faces:
                writer.write("f {} {} {}\n".format(f[0], f[1], f[2]))

def generate_mesh(cellimage, channel=0, scaling=1):
    cell = zoom(cellimage.get_image_data(out_orientation="ZYX", C=channel), [1, scaling, scaling])
    new_image = aicsImage.AICSImage(cell, dims="ZYX")

    # Use marching cubes to obtain the surface mesh of the membrane wall
    # Use the spacing parameter to "zoom" the size of the mesh
    verts, faces, normals, values = measure.marching_cubes(cell, 0)

    return CellMesh(verts, faces, normals, values, new_image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate meshes for a cell")
    parser.add_argument("input", type=str, help="the ometif file that contains the necessary cell data")

    args = parser.parse_args()
    cell_image = aicsImage.AICSImage(args.input)
    mesh = generate_mesh(cell_image, channel=3, scaling=.1)
    mesh.save_as_obj("./test_file.obj")
