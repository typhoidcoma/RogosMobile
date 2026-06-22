"""
Attach URogoGaitComponent to BP_RogoBot (idempotent). Leg config defaults come from the
C++ constructor (hip_FL/FR/BL/BR, diagonal-trot offsets), so no per-property setup here.
Run in-editor:  python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/attach_gait_component.py
"""
import unreal
BP_PATH="/Game/RogoBot/Character/BP_RogoBot"
bp=unreal.load_asset(BP_PATH)
subsys=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles=subsys.k2_gather_subobject_data_for_blueprint(bp)

# already present?
def comp_name(h):
    d=subsys.k2_find_subobject_data_from_handle(h)
    o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
    return o.get_class().get_name() if o else ""
if any("RogoGaitComponent" in comp_name(h) for h in handles):
    print("RogoGaitComponent already present -> nothing to do"); raise SystemExit

root=handles[0]  # actor/root handle
new_handle, fail=subsys.add_new_subobject(unreal.AddNewSubobjectParams(
    parent_handle=root, new_class=unreal.RogoGaitComponent, blueprint_context=bp))
if str(fail):
    print("ADD FAILED:", fail); raise SystemExit
try: subsys.rename_subobject(new_handle, unreal.Text("RogoGait"))
except Exception as e: print("rename skipped:", e)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
print("RogoGaitComponent attached to BP_RogoBot")
