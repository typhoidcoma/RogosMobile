import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if les.is_in_play_in_editor():
    print("already in PIE")
else:
    les.editor_play_simulate()
    print("SIMULATE STARTED")
