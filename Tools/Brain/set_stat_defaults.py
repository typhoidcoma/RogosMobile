import unreal
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class())
defs={"SenseRange":350.0,"WanderStrength":0.4,"MoveSpeed":600.0,"WanderAngle":0.0,"ScrambleFactor":1.0}
for k,v in defs.items():
    cdo.set_editor_property(k, v)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("defaults:", {k: cdo.get_editor_property(k) for k in defs})
