import omni.usd
from pxr import UsdGeom, UsdPhysics, Gf, Vt
import math
import numpy as np

particle_sizes = {
    "large":  0.02,
    "medium": 0.017,
    "small":  0.015
}
max_size = max(particle_sizes.values())

stage = omni.usd.get_context().get_stage()

prim = stage.GetPrimAtPath('/World/Cube')
translate = prim.GetAttribute('xformOp:translate').Get()
scale = prim.GetAttribute('xformOp:scale').Get()

num_x = math.floor(scale[0] / (2 * max_size))
num_y = math.floor(scale[1] / (2 * max_size))
num_z = math.floor(scale[2] / (2 * max_size))

interval_x = scale[0] / num_x
interval_y = scale[1] / num_y
interval_z = scale[2] / num_z

min_coords = translate - scale * 0.5

stage.RemovePrim('/World/Cube')

pi_path = '/World/Particles'
instancer = UsdGeom.PointInstancer.Define(stage, pi_path)

phi = (1 + math.sqrt(5)) / 2.0
ico_verts = np.array([
    (-1,  phi,  0),
    ( 1,  phi,  0),
    (-1, -phi,  0),
    ( 1, -phi,  0),
    ( 0, -1,  phi),
    ( 0,  1,  phi),
    ( 0, -1, -phi),
    ( 0,  1, -phi),
    ( phi,  0, -1),
    ( phi,  0,  1),
    (-phi,  0, -1),
    (-phi,  0,  1),
], dtype=float)
ico_verts = np.array([v / np.linalg.norm(v) for v in ico_verts])

ico_faces = [
    [0, 11,  5], [0,  5,  1], [0,  1,  7], [0,  7, 10], [0, 10, 11],
    [1,  5,  9], [5, 11,  4], [11, 10,  2], [10,  7,  6], [7,  1,  8],
    [3,  9,  4], [3,  4,  2], [3,  2,  6], [3,  6,  8], [3,  8,  9],
    [4,  9,  5], [2,  4, 11], [6,  2, 10], [8,  6,  7], [9,  8,  1],
]

d_verts = []
for face in ico_faces:
    pts = [ico_verts[i] for i in face]
    centroid = np.mean(pts, axis=0)
    centroid = centroid / np.linalg.norm(centroid)
    d_verts.append(tuple(centroid))

d_faces = [
    [0,  1,  2,  3,  4],
    [1,  5, 19,  9,  2],
    [17, 12, 11, 16,  7],
    [12, 13, 14, 10, 11],
    [16, 11, 10, 15,  6],
    [6,  15,  5,   1,  0],
    [8,  18, 13,  12, 17],
    [3,   2,   9,  18,  8],
    [9,  19, 14,  13, 18],
    [10, 14, 19,   5, 15],
    [4,   3,   8,  17,  7],
    [7,   16,  6,   0,  4],
]

proto_paths = []

d_verts_scaled = [Gf.Vec3f(*(np.array(v) * particle_sizes["large"])) for v in d_verts]

mesh_dode = UsdGeom.Mesh.Define(stage, f"{pi_path}/ProtoDodecahedron")
mesh_dode.CreatePointsAttr(Vt.Vec3fArray(d_verts_scaled))
mesh_dode.CreateFaceVertexCountsAttr(Vt.IntArray([5] * len(d_faces)))

flat_dode_indices = []
for face in d_faces:
    flat_dode_indices.extend(face)
mesh_dode.CreateFaceVertexIndicesAttr(Vt.IntArray(flat_dode_indices))

face_normals_dode = []
for face in d_faces:
    p0 = d_verts_scaled[face[0]]
    p1 = d_verts_scaled[face[1]]
    p2 = d_verts_scaled[face[2]]
    n = Gf.Cross(p1 - p0, p2 - p0).GetNormalized()
    for _ in range(5):
        face_normals_dode.append(n)
mesh_dode.CreateNormalsAttr(Vt.Vec3fArray(face_normals_dode))
mesh_dode.SetNormalsInterpolation("faceVarying")
mesh_dode.CreateDoubleSidedAttr().Set(True)
sand_col = Gf.Vec3f(0.35, 0.35, 0.35)
mesh_dode.CreateDisplayColorAttr(Vt.Vec3fArray([sand_col]))

UsdPhysics.CollisionAPI.Apply(mesh_dode.GetPrim())
UsdPhysics.RigidBodyAPI.Apply(mesh_dode.GetPrim())
UsdPhysics.MassAPI.Apply(mesh_dode.GetPrim())
proto_paths.append(mesh_dode.GetPath())

d_ico_scaled = [Gf.Vec3f(*(v * particle_sizes["medium"])) for v in ico_verts]

mesh_ico = UsdGeom.Mesh.Define(stage, f"{pi_path}/ProtoIcosahedron")
mesh_ico.CreatePointsAttr(Vt.Vec3fArray(d_ico_scaled))
mesh_ico.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(ico_faces)))

flat_ico_indices = []
for face in ico_faces:
    flat_ico_indices.extend(face)
mesh_ico.CreateFaceVertexIndicesAttr(Vt.IntArray(flat_ico_indices))

face_normals_ico = []
for face in ico_faces:
    p0 = d_ico_scaled[face[0]]
    p1 = d_ico_scaled[face[1]]
    p2 = d_ico_scaled[face[2]]
    n = Gf.Cross(p1 - p0, p2 - p0).GetNormalized()
    for _ in range(3):
        face_normals_ico.append(n)
mesh_ico.CreateNormalsAttr(Vt.Vec3fArray(face_normals_ico))
mesh_ico.SetNormalsInterpolation("faceVarying")
mesh_ico.CreateDoubleSidedAttr().Set(True)
mesh_ico.CreateDisplayColorAttr(Vt.Vec3fArray([sand_col]))

UsdPhysics.CollisionAPI.Apply(mesh_ico.GetPrim())
UsdPhysics.RigidBodyAPI.Apply(mesh_ico.GetPrim())
UsdPhysics.MassAPI.Apply(mesh_ico.GetPrim())
proto_paths.append(mesh_ico.GetPath())

mesh_sphere = UsdGeom.Sphere.Define(stage, f"{pi_path}/ProtoSphere")
mesh_sphere.GetRadiusAttr().Set(particle_sizes["small"])
mesh_sphere.CreateDisplayColorAttr(Vt.Vec3fArray([sand_col]))

UsdPhysics.CollisionAPI.Apply(mesh_sphere.GetPrim())
UsdPhysics.RigidBodyAPI.Apply(mesh_sphere.GetPrim())
UsdPhysics.MassAPI.Apply(mesh_sphere.GetPrim())
proto_paths.append(mesh_sphere.GetPath())

instancer.CreatePrototypesRel().SetTargets(proto_paths)

particle_positions = []
proto_indices = []

for i in range(num_x):
    for j in range(num_y):
        for k in range(num_z):
            worldPos = Gf.Vec3f(
                min_coords[0] + (i + 0.5) * interval_x,
                min_coords[1] + (j + 0.5) * interval_y,
                min_coords[2] + (k + 0.5) * interval_z
            )
            particle_positions.append(worldPos)
            proto_indices.append((i + j + k) % 3)

count = len(particle_positions)

instancer.CreatePositionsAttr().Set(particle_positions)

orientations = Vt.QuathArray([Gf.Quath(1.0, 0.0, 0.0, 0.0)] * count)
instancer.CreateOrientationsAttr().Set(orientations)

scales_attr = Vt.Vec3fArray([Gf.Vec3f(1.0, 1.0, 1.0)] * count)
instancer.CreateScalesAttr().Set(scales_attr)

instancer.CreateProtoIndicesAttr().Set(Vt.IntArray(proto_indices))

print(f"Generated {count} sand-colored particles under '/World/Particles':")
print(f"  Large = Dodecahedron, radius {particle_sizes['large']}")
print(f"  Medium = Icosahedron, radius {particle_sizes['medium']}")
print(f"  Small = Sphere, radius {particle_sizes['small']}")
