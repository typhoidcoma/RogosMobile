"""
Creates ABP_RogoBot (Animation Blueprint) targeting SK_RogoBot_Skeleton.
The AnimGraph wiring (Control Rig node -> Output Pose) is done separately.
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/make_animbp.py
"""
import unreal

SKEL = "/Game/RogoBot/Anim/SK_RogoBot_Skeleton"
PKG  = "/Game/RogoBot/Anim"
NAME = "ABP_RogoBot"
full = PKG + "/" + NAME

EAL = unreal.EditorAssetLibrary
if EAL.does_asset_exist(full):
    EAL.delete_asset(full)
    print("deleted existing", full)

skel = EAL.load_asset(SKEL)
factory = unreal.AnimBlueprintFactory()
factory.set_editor_property("target_skeleton", skel)

at = unreal.AssetToolsHelpers.get_asset_tools()
abp = at.create_asset(NAME, PKG, unreal.AnimBlueprint, factory)
print("created:", abp)
EAL.save_loaded_asset(abp)
print("DONE make_animbp")
