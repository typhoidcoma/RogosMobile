import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
if not bot: print("NO BOT"); raise SystemExit
v=bot.get_velocity(); spd=(v.x**2+v.y**2)**0.5
m=bot.get_component_by_class(unreal.SkeletalMeshComponent)
out=[]
for L in ("FL","FR","BL","BR"):
    t=m.get_socket_transform("ankle_"+L, unreal.RelativeTransformSpace.RTS_WORLD).translation
    out.append("%s(%.0f,%.0f,%.0f)"%(L,t.x,t.y,t.z))
print("spd=%.0f | "%spd + " ".join(out))
