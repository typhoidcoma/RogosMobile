"""Create BP_RogoGameMode: DefaultPawn=BP_CameraPawn, PlayerController=plain PlayerController."""
import unreal
PKG="/Game/RogoBot"; NAME="BP_RogoGameMode"; full=PKG+"/"+NAME
EAL=unreal.EditorAssetLibrary
if EAL.does_asset_exist(full): EAL.delete_asset(full); print("deleted existing")
at=unreal.AssetToolsHelpers.get_asset_tools()
f=unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.GameModeBase)
bp=at.create_asset(NAME, PKG, unreal.Blueprint, f)
cdo=unreal.get_default_object(bp.generated_class())
cam=unreal.load_object(None,"/Game/RogoBot/Camera/BP_CameraPawn.BP_CameraPawn_C")
cdo.set_editor_property("default_pawn_class", cam)
cdo.set_editor_property("player_controller_class", unreal.PlayerController)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_loaded_asset(bp)
print("GameMode created; DefaultPawn=", cdo.get_editor_property("default_pawn_class"),
      "Controller=", cdo.get_editor_property("player_controller_class"))
