"""
Adds two toggleable visual-helper mesh components to BP_RogoBot:
  - FrontArrow: a small red cone pointing out the bot's front (+X).
  - SenseRing: a flat translucent cyan disc at the feet, scaled to the sense radius.
Creates the two unlit materials they use. Idempotent (removes existing first).
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Brain/add_viz_meshes.py
"""
import unreal
EAL=unreal.EditorAssetLibrary
at=unreal.AssetToolsHelpers.get_asset_tools()
MEL=unreal.MaterialEditingLibrary

def make_mat(name, color, translucent, opacity=1.0):
    p="/Game/RogoBot/Viz/"+name
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m=at.create_asset(name,"/Game/RogoBot/Viz",unreal.Material,unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    if translucent: m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    c=MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -350, 0)
    c.set_editor_property("constant", color)
    MEL.connect_material_property(c, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if translucent:
        o=MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -350, 200)
        o.set_editor_property("r", opacity)
        MEL.connect_material_property(o, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m)
    return m

m_red=make_mat("M_VizArrow", unreal.LinearColor(1.0,0.03,0.03,1.0), False)
m_ring=make_mat("M_VizRing", unreal.LinearColor(0.1,0.9,1.0,1.0), True, 0.22)

cone=EAL.load_asset("/Engine/BasicShapes/Cone")
cyl=EAL.load_asset("/Engine/BasicShapes/Cylinder")
bp=EAL.load_asset("/Game/RogoBot/Character/BP_RogoBot")
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles=sds.k2_gather_subobject_data_for_blueprint(bp)
root=handles[0]

def comp_obj(h):
    return unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))

# remove existing FrontArrow/SenseRing
for h in handles:
    o=comp_obj(h)
    if o and o.get_name() in ("FrontArrow","SenseRing"):
        sds.delete_subobject(root, h, bp)

def add_mesh(name, mesh, mat, loc, rot, scale):
    params=unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp)
    h,fail=sds.add_new_subobject(params)
    sds.rename_subobject(h, unreal.Text(name))
    c=comp_obj(h)
    c.set_editor_property("static_mesh", mesh)
    c.set_material(0, mat)
    c.set_editor_property("relative_location", loc)
    c.set_editor_property("relative_rotation", rot)
    c.set_editor_property("relative_scale3d", scale)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_editor_property("can_ever_affect_navigation", False)
    c.set_editor_property("cast_shadow", False)
    print("added", name)

# cone points +Z by default -> pitch +90 to point +X (forward); small
add_mesh("FrontArrow", cone, m_red, unreal.Vector(70,0,110), unreal.Rotator(0,90,0), unreal.Vector(0.35,0.35,0.7))
# flat disc at feet; cylinder radius 50 -> scale 7 = radius 350 (overwritten at runtime)
add_mesh("SenseRing", cyl, m_ring, unreal.Vector(0,0,-86), unreal.Rotator(0,0,0), unreal.Vector(7.0,7.0,0.02))

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("DONE add_viz_meshes")
