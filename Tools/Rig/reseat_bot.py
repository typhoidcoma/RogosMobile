import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if "RogoBot" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(700,-300,120), False, True)
        print("moved bot to", a.get_actor_location())
