import unreal
bp=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class())
# MoveSpeed 150 (was 600): the Locomotor gait is tuned for SpeedMax 160, so 600
# saturated the gait (feet skated) and the body lagged the capsule. 150 keeps the
# legs in step. NOTE: a future speed upgrade must also raise the Locomotor
# Movement.SpeedMax/PhaseSpeedMax (build_rig.py) so the gait stays matched.
defs={"SenseRange":350.0,"WanderStrength":0.4,"MoveSpeed":150.0,"WanderAngle":0.0,"ScrambleFactor":1.0}
for k,v in defs.items():
    cdo.set_editor_property(k, v)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("defaults:", {k: cdo.get_editor_property(k) for k in defs})
