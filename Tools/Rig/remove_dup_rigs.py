"""
BP_RogoBot accumulated 3 empty ControlRigComponents (ControlRig/1/2) from
repeated rig-build runs. None has a control rig assigned; the real rig +
foot grounding run through ABP_RogoBot's Control Rig node (ABP depends on
CR_RogoBot). These actor components do nothing -> remove all 3.
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/remove_dup_rigs.py
"""
import unreal
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles=sds.k2_gather_subobject_data_for_blueprint(bp)
root=handles[0]
removed=0
for h in handles:
    o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
    if o and isinstance(o, unreal.ControlRigComponent):
        sds.delete_subobject(root, h, bp); removed+=1; print("removed", o.get_name())
print("removed %d ControlRigComponents"%removed)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
# verify
left=[unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
      for h in sds.k2_gather_subobject_data_for_blueprint(bp)]
print("ControlRigComponents remaining:", sum(1 for o in left if o and isinstance(o,unreal.ControlRigComponent)))
print("DONE")
