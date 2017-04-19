import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure

from imageio import omeTifReader
import thumbnailGenerator


cell = omeTifReader.OmeTifReader(
    "/data/aics/software_it/danielt/images/AICS/bisque/20160705_I01/20160705_I01_001_3.ome.tif"
).load()[0, :, 4]

cell = thumbnailGenerator.resize_cyx_image(cell, (cell.shape[0], cell.shape[1] // 16, cell.shape[2] // 16))

# Use marching cubes to obtain the surface mesh of the membrane wall
verts, faces = measure.marching_cubes(cell, 0)

# Display resulting triangular mesh using Matplotlib. This can also be done
# with mayavi (see skimage.measure.marching_cubes docstring).
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# Fancy indexing: `verts[faces]` to generate a collection of triangles
mesh = Poly3DCollection(verts[faces])
mesh.set_edgecolor('k')
ax.add_collection3d(mesh)

ax.set_xlim(0, cell.shape[0])
ax.set_ylim(0, cell.shape[1])
ax.set_zlim(0, cell.shape[2])

plt.tight_layout()
plt.show()