import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
l=bot.get_actor_location(); v=bot.get_velocity()
cm=bot.get_component_by_class(unreal.CharacterMovementComponent)
m=bot.get_component_by_class(unreal.SkeletalMeshComponent)
body=m.get_socket_location("body")
# expected body z if rigidly tracking capsule: capsule center + ~ (body bone is ~ +? above feet)
print("capZ=%.0f bodyZ=%.0f vel.z=%.0f mode=%s | body-lag(bodyZ-capZ)=%.0f"%(l.z, body.z, v.z, str(cm.get_editor_property("movement_mode")).split('.')[-1], body.z-l.z))
