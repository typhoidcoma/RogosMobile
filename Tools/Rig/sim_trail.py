import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
l=bot.get_actor_location(); v=bot.get_velocity(); spd=(v.x**2+v.y**2)**0.5
m=bot.get_component_by_class(unreal.SkeletalMeshComponent)
b=m.get_socket_location("body")
# horizontal lag of body behind capsule (in the direction of travel)
lagXY=((b.x-l.x)**2+(b.y-l.y)**2)**0.5
fz={L:round(m.get_socket_location("ankle_"+L).z,1) for L in ("FL","FR","BL","BR")}
print("spd=%.0f | body-vs-cap horiz lag=%.1f (dz=%.0f) | feetZ %s"%(spd, lagXY, b.z-l.z, fz))
