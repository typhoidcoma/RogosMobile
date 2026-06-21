import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
cm=bot.get_component_by_class(unreal.CharacterMovementComponent)
cm.set_editor_property("max_walk_speed", 0.0)
cm.stop_movement_immediately()
print("frozen")
