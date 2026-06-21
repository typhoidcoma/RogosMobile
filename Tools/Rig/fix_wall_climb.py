"""
Stop the bot gliding up vertical walls.

Cause: the capsule has a rounded (hemispherical) base. When it presses against a
vertical wall edge/corner, the contact normal is angled, not horizontal, so
CharacterMovement's floor check reads it as "walkable floor" (it's within the
44.76 walkable angle) and the bot steps up the wall. Enabling
bUseFlatBaseForFloorChecks makes the floor test use a flat capsule base, so a
vertical wall yields a horizontal normal -> not walkable -> the bot is stopped.

Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/fix_wall_climb.py
"""
import unreal

bp = unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
cdo = unreal.get_default_object(bp.generated_class())
cm = next(iter(cdo.get_components_by_class(unreal.CharacterMovementComponent)))
cm.set_editor_property("use_flat_base_for_floor_checks", True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("use_flat_base_for_floor_checks ->", cm.get_editor_property("use_flat_base_for_floor_checks"))
