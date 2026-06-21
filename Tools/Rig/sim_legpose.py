import unreal
ws = unreal.EditorLevelLibrary.get_game_world()
bot=None
cls=unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")
for a in unreal.GameplayStatics.get_all_actors_of_class(ws, cls):
    bot=a; break
if not bot:
    print("NO BOT")
else:
    mesh=bot.get_component_by_class(unreal.SkeletalMeshComponent)
    loc=bot.get_actor_location(); v=bot.get_velocity()
    spd=(v.x**2+v.y**2+v.z**2)**0.5
    print("loc z=%.1f speed=%.1f" % (loc.z, spd))
    for L in ["FL","BL"]:
        row=[]
        for b in ["hip_"+L,"knee_"+L,"ankle_"+L]:
            t=mesh.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_WORLD)
            row.append("%s=%.1f"%(b,t.translation.z))
        print("  "+"  ".join(row))
