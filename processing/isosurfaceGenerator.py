import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure
from skimage.draw import ellipsoid

from imageio import omeTifReader


cell = omeTifReader.OmeTifReader(
    "/data/aics/software_it/danielt/images/AICS/bisque/20160705_I01/20160705_I01_001_3.ome.tif"
).load()

memb_seg = np.transpose(cell[0, :, 4], (2, 1, 0))
memb_seg_max = np.max(memb_seg)

# Generate a level set about zero of two identical ellipsoids in 3D
ellip_base = ellipsoid(6, 10, 16, levelset=True)
ellip_double = np.concatenate((ellip_base[:-1, ...],
                               ellip_base[2:, ...]), axis=0)

# Use marching cubes to obtain the surface mesh of these ellipsoids
verts, faces = measure.marching_cubes(memb_seg, 0)

# Display resulting triangular mesh using Matplotlib. This can also be done
# with mayavi (see skimage.measure.marching_cubes docstring).
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# Fancy indexing: `verts[faces]` to generate a collection of triangles
mesh = Poly3DCollection(verts[faces])
# mesh.set_edgecolor('k')
ax.add_collection3d(mesh)

ax.set_xlim(0, memb_seg.shape[0])  # a = 6 (times two for 2nd ellipsoid)
ax.set_ylim(0, memb_seg.shape[1])  # b = 10
ax.set_zlim(0, memb_seg.shape[2])  # c = 16

plt.tight_layout()
plt.show()