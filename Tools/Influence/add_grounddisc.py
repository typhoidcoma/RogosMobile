"""
Adds a flat translucent GroundDisc to BP_InfluenceBox so designers can SEE the
ground footprint where the bot reacts (the floating sphere alone is hard to place).
RefreshVisuals (run in the construction script) colors it by mode, sizes it to
Radius, and snaps it to the ground under the field. Idempotent.
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Influence/add_grounddisc.py
"""
import unreal
EAL=unreal.EditorAssetLibrary
bp=EAL.load_asset("/Game/RogoBot/Influence/BP_InfluenceBox")
mat=EAL.load_asset("/Game/RogoBot/Influence/M_InfluenceRange")
cyl=EAL.load_asset("/Engine/BasicShapes/Cylinder")
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles=sds.k2_gather_subobject_data_for_blueprint(bp)
root=handles[0]
def comp_obj(h): return unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
# remove existing GroundDisc (idempotent)
for h in handles:
    o=comp_obj(h)
    if o and o.get_name()=="GroundDisc":
        sds.delete_subobject(root, h, bp)
params=unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp)
h,fail=sds.add_new_subobject(params)
sds.rename_subobject(h, unreal.Text("GroundDisc"))
c=comp_obj(h)
c.set_editor_property("static_mesh", cyl)
c.set_material(0, mat)
c.set_editor_property("relative_scale3d", unreal.Vector(7.0,7.0,0.02))  # overwritten by RefreshVisuals
c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
c.set_editor_property("can_ever_affect_navigation", False)
c.set_editor_property("cast_shadow", False)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/RogoBot/Influence/BP_InfluenceBox", only_if_is_dirty=False)
print("added GroundDisc")
