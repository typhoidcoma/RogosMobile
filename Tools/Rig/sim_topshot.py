import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
l=bot.get_actor_location()
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(l.x, l.y, l.z+260), unreal.Rotator(-90,0,0))
unreal.AutomationLibrary.take_high_res_screenshot(700,700,"i:/Projects/Unreal/RogosMobile/Tools/Rig/_stance.png")
print("shot at bot", round(l.x),round(l.y),round(l.z))
