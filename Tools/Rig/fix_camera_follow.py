"""Raise BP_CameraPawn FollowSpeed so the lazy-follow keeps up with the bot.
At FollowSpeed=5 the camera lagged ~60+ units behind a 300 u/s bot and only
caught up once the bot stopped at the safe zone. 12 -> ~25 unit lag (tight but
still lazy)."""
import unreal
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Camera/BP_CameraPawn")
cdo=unreal.get_default_object(bp.generated_class())
cdo.set_editor_property("FollowSpeed", 12.0)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Camera/BP_CameraPawn", only_if_is_dirty=False)
print("FollowSpeed ->", cdo.get_editor_property("FollowSpeed"))
