"""
Builds CR_RogoBot's forward-solve graph: a procedural quadruped gait.
Run in-editor:  python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/build_rig.py

Structure (forward solve):
  BeginExecution -> RigUnit_Locomotor -> 4x TwoBoneIK (one per leg)
  Locomotor (RootControl=body_ctrl, Pelvis=body, 4 FootSets w/ ankle bones, diagonal trot)
    outputs FeetTransforms[] -> ArrayGetAtIndex(i) -> TwoBoneIK[i].Effector
  TwoBoneIK bends hip->knee->ankle to reach each foot goal.
Idempotent: clears existing nodes + body_ctrl first.
"""
import unreal
cr=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Anim/CR_RogoBot")
hier=cr.get_hierarchy(); hc=cr.get_hierarchy_controller(); ctrl=cr.get_controller_by_name("RigVMModel")
EK=unreal.RigElementKey; ET=unreal.RigElementType
def bone(n): return EK(type=ET.BONE, name=n)
LEGS=["FL","FR","BL","BR"]; phases={"FL":0.0,"FR":0.5,"BL":0.5,"BR":0.0}

# ---- clear (idempotent) ----
for n in list(ctrl.get_graph().get_nodes()):
    try: ctrl.remove_node(n)
    except Exception: pass
for cn in ("body_ctrl","root_ctrl"):
    ck=EK(type=ET.CONTROL, name=cn)
    try:
        if hier.contains(ck): hc.remove_element(ck)
    except Exception: pass

# ---- root_ctrl control at the ROOT bone (ground level, z~0) ----
# The Locomotor's RootControl is its GROUND/floor reference for foot placement,
# NOT the pelvis. Anchoring it at the root bone keeps feet on the floor; the
# pelvis (body bone) is handled separately by PelvisSettings.
st=unreal.RigControlSettings(); st.control_type=unreal.RigControlType.EULER_TRANSFORM
val=hier.make_control_value_from_euler_transform(unreal.EulerTransform(scale=[1,1,1]))
bck=hc.add_control("root_ctrl", EK(), st, val, True, True)
hier.set_control_offset_transform(bck, hier.get_global_transform(bone("root"), True), True)

# ---- BeginExecution ----
begin=ctrl.add_unit_node_with_defaults(unreal.RigUnit_BeginExecution.static_struct(),
        unreal.RigUnit_BeginExecution().export_text(), 'Execute', unreal.Vector2D(-700,0))

# ---- Locomotor ----
loco=unreal.RigUnit_Locomotor()
loco.root_control="root_ctrl"
pv=unreal.PelvisSettings(); pv.pelvis_bone=bone("body")
# orient_to_ground disabled: the mesh's -90 yaw maps the pelvis tilt axes wrong
# and freezes the gait at pitch -60. Foot/body slope-adapt is a separate WIP.
pv.orient_to_ground_pitch=0.0; pv.orient_to_ground_roll=0.0
loco.pelvis=pv
mv=unreal.MovementSettings()
mv.speed_min=20.0; mv.speed_max=160.0; mv.minimum_step_length=8.0
loco.movement=mv
# ground collision ON: feet trace down to whatever surface is under them (floor OR
# ramp). orient_foot_to_ground tilts each foot to plant flat on the slope.
st=unreal.StepSettings()
st.enable_ground_collision=True
st.enable_foot_collision=True
st.orient_foot_to_ground_pitch=0.0
st.orient_foot_to_ground_roll=0.0
loco.stepping=st
ln=ctrl.add_unit_node_with_defaults(loco.static_struct(), loco.export_text(), 'Execute', unreal.Vector2D(-450,0))
NP=ln.get_node_path()
ctrl.set_array_pin_size("%s.FootSets"%NP, 4)
for i,L in enumerate(LEGS):
    ctrl.set_array_pin_size("%s.FootSets.%d.Feet"%(NP,i), 1)
    ctrl.set_pin_default_value('%s.FootSets.%d.Feet.0.AnkleBone'%(NP,i), '(Type=Bone,Name="ankle_%s")'%L)
    # zero MaxHeelPeel (default Z=50 lifts the foot off the floor)
    ctrl.set_pin_default_value('%s.FootSets.%d.Feet.0.MaxHeelPeel'%(NP,i), '(X=0.000000,Y=0.000000,Z=0.000000)')
    ctrl.set_pin_default_value('%s.FootSets.%d.PhaseOffset'%(NP,i), str(phases[L]))
ctrl.add_link(begin.find_pin('ExecutePin').get_pin_path(), ln.find_pin('ExecutePin').get_pin_path())

# ---- per-leg: ArrayGetAtIndex(FeetTransforms, i) -> TwoBoneIK.Effector ----
prev=ln  # for execution chain
for i,L in enumerate(LEGS):
    hip_g=hier.get_global_transform(bone("hip_"+L), True)
    knee_g=hier.get_global_transform(bone("knee_"+L), True)
    ankle_g=hier.get_global_transform(bone("ankle_"+L), True)
    ik=unreal.RigUnit_TwoBoneIKSimplePerItem()
    ik.item_a=bone("hip_"+L); ik.item_b=bone("knee_"+L); ik.effector_item=bone("ankle_"+L)
    ik.primary_axis=knee_g.make_relative(hip_g).translation.normal()
    # NOTE: imported bones carry scale=100 (Blender m->cm baked into bone scale),
    # so make_relative().length() returns metres (0.32) not cm (32). Compute the
    # segment lengths from raw world-space translations -> scale-immune, correct cm.
    ik.item_a_length=(knee_g.translation - hip_g.translation).length()
    ik.item_b_length=(ankle_g.translation - knee_g.translation).length()
    ik.pole_vector=(knee_g.translation*3 - hip_g.translation - ankle_g.translation).normal()
    ik.pole_vector_kind=unreal.ControlRigVectorKind.LOCATION
    ik.pole_vector_space=EK(type=ET.BONE)
    ik.secondary_axis_weight=0.0
    ik.effector=ankle_g
    ikn=ctrl.add_unit_node_with_defaults(ik.static_struct(), ik.export_text(), 'Execute', unreal.Vector2D(-150, i*180-270))
    # array-get node
    gn=ctrl.add_array_node(unreal.RigVMOpCode.ARRAY_GET_AT_INDEX, "FTransform", unreal.Transform.static_struct(),
                           unreal.Vector2D(-300, i*180-270), "get_%s"%L)
    ctrl.add_link(ln.find_pin('FeetTransforms').get_pin_path(), gn.find_pin('Array').get_pin_path())
    ctrl.set_pin_default_value("%s.Index"%gn.get_node_path(), str(i))
    ctrl.add_link(gn.find_pin('Element').get_pin_path(), ikn.find_pin('Effector').get_pin_path())
    # execution chain
    ctrl.add_link(prev.find_pin('ExecutePin').get_pin_path(), ikn.find_pin('ExecutePin').get_pin_path())
    prev=ikn

unreal.EditorAssetLibrary.save_loaded_asset(cr)
print("RIG BUILT: nodes=", len(ctrl.get_graph().get_nodes()))
