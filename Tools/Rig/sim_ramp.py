import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
cls=unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")
bot=None
for a in unreal.GameplayStatics.get_all_actors_of_class(ws, cls): bot=a; break
if not bot:
    print("NO BOT")
else:
    loc=bot.get_actor_location(); v=bot.get_velocity()
    spd=(v.x**2+v.y**2)**0.5
    mesh=bot.get_component_by_class(unreal.SkeletalMeshComponent)
    bt=mesh.get_socket_transform("body", unreal.RelativeTransformSpace.RTS_WORLD)
    pitch=bt.rotation.rotator().pitch
    fz={}; fr={}
    for L in ("FL","FR","BL","BR"):
        t=mesh.get_socket_transform("ankle_"+L, unreal.RelativeTransformSpace.RTS_WORLD)
        fz[L]=round(t.translation.z,1)
        r=t.rotation.rotator(); fr[L]=(round(r.pitch),round(r.roll))
    print("capsule z=%.1f Yp=%.0f spd=%.0f | body pitch=%.1f | feetZ FL=%s FR=%s BL=%s BR=%s | FLrot=%s"%(
        loc.z, loc.y, spd, pitch, fz["FL"],fz["FR"],fz["BL"],fz["BR"], fr["FL"]))
