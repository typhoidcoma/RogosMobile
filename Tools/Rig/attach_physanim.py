"""
Attach a UPhysicalAnimationComponent to BP_RogoBot (idempotent). URogoGaitComponent finds it
at BeginPlay and uses it to motor the simulated body+legs toward the gait pose (real per-part
collision). Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/attach_physanim.py
"""
import unreal
BP_PATH="/Game/RogoBot/Character/BP_RogoBot"
bp=unreal.load_asset(BP_PATH)
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles=sds.k2_gather_subobject_data_for_blueprint(bp)

def comp_class(h):
    o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
    return o.get_class().get_name() if o else ""
if any("PhysicalAnimationComponent" in comp_class(h) for h in handles):
    print("PhysicalAnimationComponent already present -> nothing to do"); raise SystemExit

root=handles[0]
nh, fail=sds.add_new_subobject(unreal.AddNewSubobjectParams(
    parent_handle=root, new_class=unreal.PhysicalAnimationComponent, blueprint_context=bp))
if str(fail):
    print("ADD FAILED:", fail); raise SystemExit
try: sds.rename_subobject(nh, unreal.Text("PhysAnim"))
except Exception as e: print("rename skipped:", e)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
print("PhysicalAnimationComponent attached to BP_RogoBot")
