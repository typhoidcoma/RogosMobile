"""
Influence boxes are gameplay FIELDS, not navigation obstacles, but their
RangeSphere had can_ever_affect_navigation=True -> it was corrupting the navmesh
(stray elevated patches that fragment the bot's pathfinding). Turn it off on the
BP template and on every placed instance, then rebuild navigation.
"""
import unreal

# template (future instances)
cls=unreal.load_object(None,"/Game/RogoBot/Influence/BP_InfluenceBox.BP_InfluenceBox_C")
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Influence/BP_InfluenceBox")
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o=unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(sds.k2_find_subobject_data_from_handle(h))
    if o and o.get_name()=="RangeSphere":
        o.set_editor_property("can_ever_affect_navigation", False)
        print("template RangeSphere affectsNav ->", o.get_editor_property("can_ever_affect_navigation"))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Influence/BP_InfluenceBox", only_if_is_dirty=False)

# placed instances
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n=0
for a in eas.get_all_level_actors():
    if "InfluenceBox" in a.get_class().get_name():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_editor_property("can_ever_affect_navigation"):
                c.set_editor_property("can_ever_affect_navigation", False); n+=1
print("instances fixed:", n)

ws=unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(ws, "RebuildNavigation")
print("navmesh rebuild issued")
