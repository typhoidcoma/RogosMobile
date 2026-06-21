import unreal
gm=unreal.load_object(None,"/Game/RogoBot/BP_RogoGameMode.BP_RogoGameMode_C")
ws=unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
old=ws.get_editor_property("default_game_mode")
ws.set_editor_property("default_game_mode", gm)
print("WorldSettings GameModeOverride: %s -> %s" % (old, ws.get_editor_property("default_game_mode")))
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
print("level saved")
