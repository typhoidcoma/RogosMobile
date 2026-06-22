"""
Builds CR_RogoBot's forward-solve graph using the custom C++ gait node.
Run in-editor:  python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/build_rig.py

Structure (forward solve):
  BeginExecution -> RigUnit_RogoGait -> 4x TwoBoneIK (one per leg)
  RogoGait (C++, module RogosMobile) reads the owning actor's velocity, runs its own
  phase timer (cadence = Frequency), and outputs world foot targets that world-lock
  while planted -> the legs drive the motion. FeetTransforms[i] -> TwoBoneIK[i].Effector.
Idempotent: clears existing nodes first. (Replaces the old RigUnit_Locomotor build.)
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
# Clear legacy controls (older builds used root_ctrl / per-leg plant_* scratch controls;
# the gait is stateless now and needs none).
for cn in ("body_ctrl","root_ctrl")+tuple("plant_%s"%L for L in LEGS):
    ck=EK(type=ET.CONTROL, name=cn)
    try:
        if hier.contains(ck): hc.remove_element(ck)
    except Exception: pass

# rest foot drop (hip rest Z above the foot) -> flat-ground foot height. Scale-immune via world Z.
hipZ=hier.get_global_transform(bone("hip_FL"), True).translation.z
ankZ=hier.get_global_transform(bone("ankle_FL"), True).translation.z
REST_DROP=hipZ-ankZ

# ---- BeginExecution ----
begin=ctrl.add_unit_node_with_defaults(unreal.RigUnit_BeginExecution.static_struct(),
        unreal.RigUnit_BeginExecution().export_text(), 'Execute', unreal.Vector2D(-700,0))

# ---- RogoGait (custom C++ gait) ----
gait=unreal.RigUnit_RogoGait()
gn=ctrl.add_unit_node_with_defaults(gait.static_struct(), gait.export_text(), 'Execute', unreal.Vector2D(-450,0))
GP=gn.get_node_path()
ctrl.set_pin_default_value("%s.Frequency"%GP, "1.5")
ctrl.set_pin_default_value("%s.StanceFraction"%GP, "0.6")
ctrl.set_pin_default_value("%s.StepHeight"%GP, "14.0")
ctrl.set_pin_default_value("%s.BodyBob"%GP, "6.0")
ctrl.set_pin_default_value("%s.RestDrop"%GP, str(REST_DROP))
ctrl.set_pin_default_value("%s.BodyBone"%GP, '(Type=Bone,Name="body")')
ctrl.set_array_pin_size("%s.Hips"%GP, 4)
ctrl.set_array_pin_size("%s.PhaseOffsets"%GP, 4)
for i,L in enumerate(LEGS):
    ctrl.set_pin_default_value('%s.Hips.%d'%(GP,i), '(Type=Bone,Name="hip_%s")'%L)
    ctrl.set_pin_default_value('%s.PhaseOffsets.%d'%(GP,i), str(phases[L]))
ctrl.add_link(begin.find_pin('ExecutePin').get_pin_path(), gn.find_pin('ExecutePin').get_pin_path())

# ---- body bob: SetTransform(body) <- RogoGait.BodyTransform (global) ----
# Runs BEFORE the IK legs. BodyTransform is the body's global pose + Z bob; propagating
# to children lifts the hips with it, while the IK below re-pins each ankle to its world
# FeetTransform -> body bobs, planted feet stay world-locked (legs extend/compress).
sb=unreal.RigUnit_SetTransform()
sb.item=bone("body")
sb.space=unreal.RigVMTransformSpace.GLOBAL_SPACE
sb.propagate_to_children=True
sbn=ctrl.add_unit_node_with_defaults(sb.static_struct(), sb.export_text(), 'Execute', unreal.Vector2D(-300,150))
ctrl.add_link(gn.find_pin('ExecutePin').get_pin_path(), sbn.find_pin('ExecutePin').get_pin_path())
ctrl.add_link(gn.find_pin('BodyTransform').get_pin_path(), sbn.find_pin('Value').get_pin_path())

# ---- per-leg: ArrayGetAtIndex(FeetTransforms, i) -> TwoBoneIK.Effector ----
prev=sbn
for i,L in enumerate(LEGS):
    hip_g=hier.get_global_transform(bone("hip_"+L), True)
    knee_g=hier.get_global_transform(bone("knee_"+L), True)
    ankle_g=hier.get_global_transform(bone("ankle_"+L), True)
    ik=unreal.RigUnit_TwoBoneIKSimplePerItem()
    ik.item_a=bone("hip_"+L); ik.item_b=bone("knee_"+L); ik.effector_item=bone("ankle_"+L)
    ik.primary_axis=knee_g.make_relative(hip_g).translation.normal()
    # bones carry scale=100 -> compute segment lengths from world translations (scale-immune).
    ik.item_a_length=(knee_g.translation - hip_g.translation).length()
    ik.item_b_length=(ankle_g.translation - knee_g.translation).length()
    ik.pole_vector=(knee_g.translation*3 - hip_g.translation - ankle_g.translation).normal()
    ik.pole_vector_kind=unreal.ControlRigVectorKind.LOCATION
    ik.pole_vector_space=EK(type=ET.BONE)
    ik.secondary_axis_weight=0.0
    ik.effector=ankle_g
    ikn=ctrl.add_unit_node_with_defaults(ik.static_struct(), ik.export_text(), 'Execute', unreal.Vector2D(-150, i*180-270))
    g=ctrl.add_array_node(unreal.RigVMOpCode.ARRAY_GET_AT_INDEX, "FTransform", unreal.Transform.static_struct(),
                          unreal.Vector2D(-300, i*180-270), "get_%s"%L)
    ctrl.add_link(gn.find_pin('FeetTransforms').get_pin_path(), g.find_pin('Array').get_pin_path())
    ctrl.set_pin_default_value("%s.Index"%g.get_node_path(), str(i))
    ctrl.add_link(g.find_pin('Element').get_pin_path(), ikn.find_pin('Effector').get_pin_path())
    ctrl.add_link(prev.find_pin('ExecutePin').get_pin_path(), ikn.find_pin('ExecutePin').get_pin_path())
    prev=ikn

unreal.EditorAssetLibrary.save_loaded_asset(cr)
print("RIG BUILT (RogoGait): nodes=", len(ctrl.get_graph().get_nodes()), "REST_DROP=%.1f"%REST_DROP)
