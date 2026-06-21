import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
l=bot.get_actor_location()
bot.set_actor_location(unreal.Vector(l.x, l.y, l.z+500), False, False)
cm=bot.get_component_by_class(unreal.CharacterMovementComponent)
cm.set_movement_mode(unreal.MovementMode.MOVE_FALLING)
print("lifted to", round(bot.get_actor_location().z))
