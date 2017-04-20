# author: Zach Crabtree zacharyc@alleninstitute.org

from skimage import measure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import argparse

from imageio import omeTifReader
import thumbnailGenerator


# TODO make this a little more generalizable.
# return an obj file, not these vars
# new_size should not be passed out either, that's just a convenience for the display_mesh function
def generate_mesh(ome_tif_path, scaling=1):
    cell = omeTifReader.OmeTifReader(ome_tif_path).load()[0, :, 5]
    new_size = (cell.shape[0], cell.shape[1] // scaling, cell.shape[2] // scaling)
    cell = thumbnailGenerator.resize_cyx_image(cell, new_size)

    # Use marching cubes to obtain the surface mesh of the membrane wall
    # Use the spacing parameter to "zoom" the size of the mesh
    verts, faces, normals, values = measure.marching_cubes(cell, 0)

    return verts, faces, normals, values, new_size


def display_mesh(verts, faces, size):
    # Display resulting triangular mesh using Matplotlib. This can also be done
    # with mayavi (see skimage.measure.marching_cubes docstring).
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces])
    mesh.set_edgecolor('k')
    ax.add_collection3d(mesh)

    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])
    ax.set_zlim(0, size[2])

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate meshes for a cell")
    parser.add_argument("input", type=str, help="the ometif file that contains the necessary cell data")

    args = parser.parse_args()
    ver, f, n, vals, new_size = generate_mesh(args.input, scaling=16)
    display_mesh(ver, f, new_size)
