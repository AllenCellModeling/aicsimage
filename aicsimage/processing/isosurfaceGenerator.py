# author: Zach Crabtree zacharyc@alleninstitute.org

from skimage import measure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import argparse
import numpy as np

import cellImage
import thumbnailGenerator


class CellMesh:

    def __init__(self, verts, faces, normals, values, base_image):
        self.verts = verts
        self.faces = faces
        self.normals = normals
        self.values = values
        if not isinstance(base_image, cellImage.CellImage):
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

        ax.set_xlim(0, self.image_stack.shape[0])
        ax.set_ylim(0, self.image_stack.shape[1])
        ax.set_zlim(0, self.image_stack.shape[2])

        plt.tight_layout()
        plt.show()


def generate_mesh(cellimage, scaling=1):
    cell = cellimage.get_image_data(out_orientation="XYZCT")
    new_size = (cell.shape[0], cell.shape[1] // scaling, cell.shape[2] // scaling)
    cell = thumbnailGenerator.resize_cyx_image(cell, new_size)

    # Use marching cubes to obtain the surface mesh of the membrane wall
    # Use the spacing parameter to "zoom" the size of the mesh
    verts, faces, normals, values = measure.marching_cubes(cell, 0)

    return CellMesh(verts, faces, normals, values, cellimage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate meshes for a cell")
    parser.add_argument("input", type=str, help="the ometif file that contains the necessary cell data")

    args = parser.parse_args()
    cell_image = cellImage.CellImage(args.input)
    mesh = generate_mesh(cell_image, scaling=16)
    mesh.display()
