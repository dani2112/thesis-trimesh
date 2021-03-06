"""
scan_register.py
-------------

Create some simulated 3D scan data and register 
it to a "truth" mesh.
"""

import trimesh
import numpy as np


def simulated_brick(face_count, extents, noise, max_iter=10):
    """
    Produce a mesh that is a rectangular solid with noise
    with a random transform.

    Parameters
    -------------
    face_count : int
      Approximate number of faces desired
    extents : (n,3) float
      Dimensions of brick
    noise : float
      Magnitude of vertex noise to apply
    """

    # create the mesh as a simple box
    mesh = trimesh.creation.box(extents=extents)

    # add some systematic error pre- tesselation
    mesh.vertices[0] += mesh.vertex_normals[0] + (noise * 2)
    
    # subdivide until we have more faces than we want
    for i in range(max_iter):
        if len(mesh.vertices) > face_count:
            break
        mesh = mesh.subdivide()

    # apply tesselation and random noise
    mesh = mesh.permutate.noise(noise)

    # randomly rotation with translation
    transform = trimesh.transformations.random_rotation_matrix()
    transform[:3, 3] = (np.random.random(3) - .5) * 1000
    
    mesh.apply_transform(transform)
    
    return mesh


if __name__ == '__main__':
    # print log messages to terminal
    trimesh.util.attach_to_log()
    
    # the size of our boxes
    extents = [6, 12, 2]
    
    # create a simulated brick with noise and random transform
    scan = simulated_brick(face_count=5000,
                           extents=extents,
                           noise=.05)

    # create a "true" mesh
    truth = trimesh.creation.box(extents=extents)

    # (4, 4) float homogenous transform from truth to scan
    truth_to_scan, cost = truth.register(scan)

    print("centroid distance pre-registration:",
          np.linalg.norm(truth.centroid - scan.centroid))

    # apply the registration transform
    truth.apply_transform(truth_to_scan)
    print("centroid distance post-registration:",
          np.linalg.norm(truth.centroid - scan.centroid))
    
    # find the distance from the truth mesh to each scan vertex
    distance = truth.nearest.on_surface(scan.vertices)[1]
    # 0.0 - 1.0 distance fraction
    fraction = distance / distance.max()

    # color the mesh by distance from truth with
    # linear interpolation between two colors
    colors = ([255,0,0,255] * fraction.reshape((-1,1)) +
              [0,255,0,255] * (1 - fraction).reshape((-1,1)))
    # apply the vertex colors to the scan mesh
    scan.visual.vertex_colors = colors.astype(np.uint8)

    # print some quick statistics about the mesh
    print('distance max:', distance.max())
    print('distance mean:', distance.mean())
    print('distance STD:', distance.std())
    
    # export result with vertex colors for meshlab
    scan.export('scan_new.ply')

    # show in a pyglet window
    scan.show()

    
    
    
