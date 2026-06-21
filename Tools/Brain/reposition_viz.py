"""
Reposition the existing FrontArrow + SenseRing viz components for the matched
capsule (half-height 59 -> actor rests at ground+59). Materials untouched.
  FrontArrow: hug the upper-front of the body (was floating +110 -> parallax).
  SenseRing : sit at the feet (was -86 -> ~27 under ground).
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Brain/reposition_viz.py
"""
import unreal
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
    if not o: continue
    n=o.get_name()
    if n.startswith("FrontArrow"):
        o.set_editor_property("relative_location", unreal.Vector(40,0,35))
        o.set_editor_property("relative_scale3d", unreal.Vector(0.3,0.3,0.6))
        print("FrontArrow -> (40,0,35) scale(0.3,0.3,0.6)")
    elif n.startswith("SenseRing"):
        o.set_editor_property("relative_location", unreal.Vector(0,0,-58))
        print("SenseRing -> (0,0,-58)")
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("DONE")
