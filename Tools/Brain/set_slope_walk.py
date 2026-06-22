"""Raise BP_RogoBot's walkable floor angle so it can climb the test ramps (45 deg).
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Brain/set_slope_walk.py"""
import unreal
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
cdo=unreal.get_default_object(bp.generated_class())
cm=next(iter(cdo.get_components_by_class(unreal.CharacterMovementComponent)))
# set_walkable_floor_angle recomputes the cached WalkableFloorZ (a plain property set wouldn't).
try:
    cm.set_walkable_floor_angle(50.0)
except Exception:
    cm.set_editor_property("walkable_floor_angle", 50.0)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("walkable_floor_angle:", cm.get_editor_property("walkable_floor_angle"),
      "max_step_height:", cm.get_editor_property("max_step_height"))
