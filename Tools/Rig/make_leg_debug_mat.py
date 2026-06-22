"""
Creates M_LegDebug (/Game/RogoBot/Viz/M_LegDebug): an unlit material that shows the mesh's
VertexColor as Emissive. Paired with URogoGaitComponent's per-leg vertex-color override so
each leg renders a distinct test color. Idempotent (reuses if it exists).
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/make_leg_debug_mat.py
"""
import unreal
EAL=unreal.EditorAssetLibrary
at=unreal.AssetToolsHelpers.get_asset_tools()
MEL=unreal.MaterialEditingLibrary

P="/Game/RogoBot/Viz/M_LegDebug"
if EAL.does_asset_exist(P):
    print("M_LegDebug already exists -> reusing"); raise SystemExit
m=at.create_asset("M_LegDebug","/Game/RogoBot/Viz",unreal.Material,unreal.MaterialFactoryNew())
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
# VertexColor node -> Emissive (RGB) so the per-vertex override drives the look.
vc=MEL.create_material_expression(m, unreal.MaterialExpressionVertexColor, -350, 0)
MEL.connect_material_property(vc, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.recompile_material(m); EAL.save_loaded_asset(m)
print("M_LegDebug created at", P)
