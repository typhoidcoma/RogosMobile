"""
Blender generator for the RogoBot quadruped PROXY skeletal mesh.
Builds: spherical body + single eye + 4 splayed legs (hip/knee/ankle each),
an armature with matching bone names, rigid skin weights, exports a UE FBX.

Run headless:
  "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python this.py -- <out.fbx>

Units: Blender meters == UE centimeters * 0.01 (UE FBX import gives x100 -> cm).
Bone names must match the Control Rig: root, body, hip_/knee_/ankle_<FL|FR|BL|BR>.
"""
import bpy, sys, math
from mathutils import Vector

OUT = sys.argv[-1] if "--" in sys.argv else "C:/temp/RogoBot.fbx"

# ---- wipe scene ----
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for blk in (bpy.data.meshes, bpy.data.armatures, bpy.data.objects):
    for d in list(blk):
        try: blk.remove(d)
        except Exception: pass

# ---- layout (Blender units; *100 -> UE cm) ----
BODY = Vector((0, 0, 0.70)); BODY_R = 0.45
LEGS = {'FL': (+0.28, -0.30), 'FR': (+0.28, +0.30),
        'BL': (-0.28, -0.30), 'BR': (-0.28, +0.30)}
def hip(fx, sy):   return Vector((fx,        sy,        0.58))
def knee(fx, sy):  return Vector((fx*1.05,   sy*1.55,   0.30))
def ankle(fx, sy): return Vector((fx*1.05,   sy*1.72,   0.05))

parts = []  # (object, bone_group_name)

def cyl(p1, p2, r, name):
    p1, p2 = Vector(p1), Vector(p2)
    vec = p2 - p1; length = max(vec.length, 1e-4)
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, location=(p1+p2)/2, vertices=12)
    o = bpy.context.active_object; o.name = name
    o.rotation_euler = Vector((0, 0, 1)).rotation_difference(vec).to_euler()
    return o

def sphere(loc, r, name):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=20, ring_count=12)
    o = bpy.context.active_object; o.name = name; return o

def box(loc, s, name):
    bpy.ops.mesh.primitive_cube_add(size=s, location=loc)
    o = bpy.context.active_object; o.name = name; return o

# body + eye -> "body"
parts.append((sphere(BODY, BODY_R, "Body"), "body"))
parts.append((sphere(Vector((0.46, 0, 0.74)), 0.10, "Eye"), "body"))

# legs
for L, (fx, sy) in LEGS.items():
    h, k, a = hip(fx, sy), knee(fx, sy), ankle(fx, sy)
    parts.append((cyl(h, k, 0.11, "Thigh_"+L), "hip_"+L))
    parts.append((cyl(k, a, 0.085, "Shin_"+L), "knee_"+L))
    parts.append((box(a, 0.16, "Foot_"+L), "ankle_"+L))

# ---- assign one vertex group per part, then join into one mesh ----
for o, grp in parts:
    vg = o.vertex_groups.new(name=grp)
    vg.add([v.index for v in o.data.vertices], 1.0, 'REPLACE')

bpy.ops.object.select_all(action='DESELECT')
for o, _ in parts: o.select_set(True)
body_obj = parts[0][0]
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.join()
mesh_obj = bpy.context.active_object
mesh_obj.name = "SK_RogoBot"

# ---- armature ----
arm_data = bpy.data.armatures.new("RogoArm")
arm_obj = bpy.data.objects.new("RogoArmature", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
def bone(name, head, tail, parent=None):
    b = eb.new(name); b.head = head; b.tail = tail; b.use_connect = False
    if parent: b.parent = eb[parent]
    return b
bone("root", (0, 0, 0.0), (0, 0, 0.12))
bone("body", BODY, BODY + Vector((0, 0, 0.15)), "root")
for L, (fx, sy) in LEGS.items():
    h, k, a = hip(fx, sy), knee(fx, sy), ankle(fx, sy)
    s = 1 if sy > 0 else -1
    bone("hip_"+L, h, k, "body")
    bone("knee_"+L, k, a, "hip_"+L)
    bone("ankle_"+L, a, a + Vector((0.04, s*0.04, -0.02)), "knee_"+L)
bpy.ops.object.mode_set(mode='OBJECT')

# ---- skin: parent mesh to armature (vertex groups -> bones) ----
mesh_obj.parent = arm_obj
mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
mod.object = arm_obj

# ---- export FBX for UE ----
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True); mesh_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.export_scene.fbx(
    filepath=OUT, use_selection=True,
    object_types={'ARMATURE', 'MESH'},
    add_leaf_bones=False, bake_anim=False,
    mesh_smooth_type='FACE', use_armature_deform_only=True,
)
print("EXPORTED_FBX", OUT)
