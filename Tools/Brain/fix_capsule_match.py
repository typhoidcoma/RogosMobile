"""
Reshape BP_RogoBot collision capsule to match the visible quadruped bounds.
Body (from SK_RogoBot bounds): ~118 tall, ~120 long, ~100 wide, feet at capsule bottom.
Old capsule 45 x 88(half) = 176 tall pillar -> ~60cm above the bot's head.
New: half-height 59 (matches ~118 body height), radius 50 (covers width),
mesh rel-Z -59 so feet stay at the capsule bottom (grounding preserved).
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Brain/fix_capsule_match.py
"""
import unreal
EAL=unreal.EditorAssetLibrary
bp=EAL.load_asset("/Game/RogoBot/Character/BP_RogoBot")
cdo=unreal.get_default_object(bp.generated_class())
cap=cdo.get_editor_property("capsule_component")
print("OLD cap r=%.0f hh=%.0f"%(cap.get_unscaled_capsule_radius(),cap.get_unscaled_capsule_half_height()))
# Radius trimmed (50 -> 42) now that the per-bone bodies (physical animation) do the real
# collision -> the bot gets closer to walls and the body/leg bodies become the effective contact.
# Half-height + mesh offset kept at 59 (changing them destabilised the physical sim).
cap.set_editor_property("capsule_half_height",59.0)
cap.set_editor_property("capsule_radius",42.0)
mesh=cdo.get_editor_property("mesh")
ml=mesh.get_editor_property("relative_location")
mesh.set_editor_property("relative_location",unreal.Vector(ml.x,ml.y,-59.0))
print("NEW cap r=%.0f hh=%.0f  mesh relZ=-59"%(cap.get_unscaled_capsule_radius(),cap.get_unscaled_capsule_half_height()))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/RogoBot/Character/BP_RogoBot",only_if_is_dirty=False)
print("DONE")
