"""
Switches BP_RogoBot to drive CharacterMesh0 via ABP_RogoBot (Control Rig anim node),
and removes the now-redundant RogoRig ControlRigComponent.
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/switch_to_animbp.py
"""
import unreal

BP_PATH = "/Game/RogoBot/Character/BP_RogoBot"
ABP_CLASS = "/Game/RogoBot/Anim/ABP_RogoBot.ABP_RogoBot_C"

bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
abp_class = unreal.load_object(None, ABP_CLASS)

mesh = None
rig_handle = None
all_handles = sds.k2_gather_subobject_data_for_blueprint(bp)
root_handle = all_handles[0]
for h in all_handles:
    bf = sds.k2_find_subobject_data_from_handle(h)
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(bf)
    if not o: continue
    if o.get_name() == "CharacterMesh0":
        mesh = o
    if isinstance(o, unreal.ControlRigComponent):
        rig_handle = h

# 1) point the mesh at the AnimBP
mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh.set_editor_property("anim_class", abp_class)
print("mesh anim_class ->", mesh.get_editor_property("anim_class"))

# 2) delete the redundant RogoRig component
if rig_handle is not None:
    n = sds.delete_subobject(root_handle, rig_handle, bp)
    print("deleted RogoRig component, count=", n)
else:
    print("no RogoRig to delete")

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(BP_PATH, only_if_is_dirty=False)
print("DONE switch_to_animbp")
